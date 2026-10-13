from typing import TypedDict, Optional
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage
from typing import Annotated

from langchain_core.runnables import RunnableConfig
from langchain_core.stores import InMemoryStore
from langgraph.graph import START, END, add_messages, StateGraph
from config import settings, get_settings
from langchain_core.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession
from database import DbSession
from models import DocumentChunk
from agents.rag import retrieve_chunks
from rag.security import generate_system_prompt

SYSTEM_PROMPT = {
    "role":"",
    "task":""
}


class AgentState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]
    error : Optional[str]
    retry_count : int
    model_used : str

class ProductionAgent:
    """
        Production Agent class.
    """

    def __init__(self):
        settings = get_settings() # initialize cached settings



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

        @tool
        async def retrieve_chunks_tool(client_id: int, query: str,db : AsyncSession = DbSession):
            """
            Tool used for retrieve a list of DocumentChunks from PostgresSQL database.
            args:
                db: AsyncSession ( Database session, in order to query the database)
                client_id : int

            """
            document_chunks : list[DocumentChunk] = await retrieve_chunks(db=db, client_id=client_id, query=query)
            return document_chunks

        async def llm_node(state: AgentState):

            messages = [SystemMessage(content=generate_system_prompt(role=SYSTEM_PROMPT["role"],task=SYSTEM_PROMPT["task"]))] + state["messages"]
            try:
                response = self.primary_llm.ainvoke(messages)
                return {
                    "messages":[response],
                    "model_used":self.primary_llm,
                }
            except Exception as e:
                return {
                    "error":f"Error while connecting to the primary LLM : {self.primary_llm}"
                }
        async def fallback_llm(state : AgentState):
            try:
                response = self.fallback_llm.ainvoke(state["messages"])
                return{
                    "messages":[response],
                    "model_used":self.fallback_llm,
                }
            except Exception as e:
                return {
                    "error": f"Error while connecting to the primary LLM : {self.primary_llm}"
                }


        async def _build_graph(state: AgentState):
            tools = [retrieve_chunks_tool]
            checkpointer = InMemoryStore()
            agent_builder = StateGraph(AgentState)
            agent_builder.add_node("llm_node",llm_node)
            agent_builder.add_node("")

            agent_builder.compile()


