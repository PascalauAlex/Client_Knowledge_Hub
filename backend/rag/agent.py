import json
import logging
from typing import TypedDict, Optional, Annotated

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import START, END, add_messages, StateGraph
from langgraph.prebuilt import ToolNode
from langsmith import traceable
from pydantic import BaseModel, Field
from config import get_settings
from langchain_core.tools import tool
from database import AsyncSessionLocal
from agents.rag import retrieve_chunks, format_context, build_sources
from rag.security import generate_system_prompt
from schemas import ChatSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_system_prompt_with_tool_names(tool_names: list[str]):
    return {
        "role": "You are a document assistant that answers questions about a specific client's documents.",
        "task": f"""
    Your rules:
    - Answer EXCLUSIVELY based on the context provided below. The context consists of excerpts retrieved from the client's documents.
    - If the answer is not contained in the context, say clearly that the information is not available in the documents. Do not guess, and do not use outside knowledge to fill gaps.
    - Do not invent facts, figures, dates, or names that are not present in the context.
    - When you state a fact, cite its source using the document title and page given in the header of each excerpt (e.g. "according to Annual report 2024, page 2").
    - If the context contains conflicting information, point out the conflict rather than choosing one silently.
    - Keep answers concise and grounded in the text. Quote short phrases from the context when precision matters.
    - Answer in the same language as the user's question.

    You will have to use the provided tools:
    {tool_names}
    """
    }


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    error: Optional[str]
    retry_count: int
    model_used: str
    context: str
    sources: list[dict]


class ProductionAgent:
    """
    Production Agent class.
    """

    def __init__(self):
        settings = get_settings()

        self.primary_llm = ChatOpenAI(
            name="primary_model",
            temperature=0,
            api_key=settings.openai_key,
            max_retries=0,
            model=settings.primary_model
        )
        self.fallback_llm = ChatOpenAI(
            name="secondary_model",
            temperature=0,
            api_key=settings.openai_key,
            max_retries=0,
            model=settings.secondary_model
        )
        self.max_retries = settings.max_retries

        @tool
        async def retrieve_chunks_with_sources(client_id: int, query: str) -> dict:
            """
            Tool used for retrieving context and related sources.
            :params -> client_id: int and query: str
            :returns a dictionary that contains context and related sources
            """
            async with AsyncSessionLocal() as session:
                document_chunks = await retrieve_chunks(client_id=client_id, query=query, db=session)

            formatted_context = "n/a"
            sources: list[ChatSource] = []
            if document_chunks:
                formatted_context = format_context(document_chunks)
                sources = build_sources(document_chunks)

            return {
                "context": formatted_context,
                "sources": [source.model_dump() for source in sources]
            }

        self.tools = [retrieve_chunks_with_sources]

        self.tool_names = [t.name for t in self.tools]

        system_prompt = generate_system_prompt_with_tool_names(self.tool_names)
        self.system_message = SystemMessage(
            content=generate_system_prompt(role=system_prompt["role"], task=system_prompt["task"])
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state machine."""
        tool_node = ToolNode(tools=self.tools)

        async def process_message(state: AgentState) -> dict:
            try:
                primary_llm_with_tools = self.primary_llm.bind_tools(self.tools)
                response = await primary_llm_with_tools.ainvoke(input=[self.system_message] + state["messages"])
                return {
                    "messages": [response],
                    "error": None,
                    "model_used": str(self.primary_llm.name)
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "retry_count": state["retry_count"] + 1,
                    "model_used": ""
                }

        async def try_fallback(state: AgentState) -> dict:
            try:
                fallback_llm_with_tools = self.fallback_llm.bind_tools(self.tools)
                response = await fallback_llm_with_tools.ainvoke(input=[self.system_message] + state["messages"])
                return {
                    "messages": [response],
                    "error": None,
                    "model_used": str(self.fallback_llm.name)
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "model_used": ""
                }


        async def execute_tools(state: AgentState) -> dict:
            output = await tool_node.ainvoke(state)
            tool_messages = output.get("messages", [])

            context = state.get("context", "n/a")
            sources = state.get("sources", [])

            if tool_messages:
                try:
                    # Extract the dictionary returned by retrieve_chunks_with_sources
                    payload = json.loads(tool_messages[-1].content)
                    if isinstance(payload, dict):
                        context = payload.get("context", context)
                        sources = payload.get("sources", sources)
                except Exception as e:
                    logger.warning(f"Could not parse tool output: {e}")

            return {
                "messages": tool_messages,
                "context": context,
                "sources": sources
            }

        def handle_error(state: AgentState) -> dict:
            return {
                "messages": [
                    AIMessage(content=(
                        "I'm sorry, I'm having trouble processing your request "
                        "right now. Please try again in a moment."
                    ))
                ],
                "model_used": "error_handler"
            }

        def route_after_process(state: AgentState) -> str:
            if state["messages"] and hasattr(state["messages"][-1], "tool_calls") and len(
                    state["messages"][-1].tool_calls) > 0:
                return "tool_call"
            if state.get("error") is None:
                return "done"
            elif state["retry_count"] < self.max_retries:
                return "fallback"
            else:
                return "error"

        def route_to_process_after_tool(state: AgentState) -> str:
            if state["model_used"] == str(self.fallback_llm.name):
                return "fallback"
            else:
                return "process"

        def route_after_fallback(state: AgentState) -> str:
            if state["messages"] and hasattr(state["messages"][-1], "tool_calls") and len(
                    state["messages"][-1].tool_calls) > 0:
                return "tool_call"
            if state.get("error") is None:
                return "done"
            else:
                return "error"

        # Build the graph
        graph = StateGraph(AgentState)

        # Nodes
        graph.add_node("process", process_message)
        graph.add_node("fallback", try_fallback)
        graph.add_node("error", handle_error)
        graph.add_node("tools", execute_tools)  # AgentState Custom node that actualize AgentState

        # Edges
        graph.add_edge(START, "process")
        graph.add_conditional_edges(
            "process",
            route_after_process,
            {"done": END, "fallback": "fallback", "error": "error", "tool_call": "tools"}
        )
        graph.add_conditional_edges(
            "tools",
            route_to_process_after_tool,
            {"process": "process", "fallback": "fallback"}
        )
        graph.add_conditional_edges(
            "fallback",
            route_after_fallback,
            {"done": END, "error": "error", "tool_call": "tools"}
        )
        return graph.compile()

    @traceable(name="production_rag_system")
    async def invoke(self, message: str) -> dict:
        result = await self.graph.ainvoke({
            "messages": [HumanMessage(content=message)],
            "error": None,
            "retry_count": 0,
            "model_used": "",
            "context": "n/a",
            "sources": []
        })

        # Return final answer of LLM with sources and context from AgentState
        return {
            "answer": result["messages"][-1].content,
            "sources": result.get("sources", []),
            "context": result.get("context", "n/a"),
            "model_used": result.get("model_used", "unknown"),
            "error": result.get("error", None)
        }