from typing import TypedDict, Optional

from langchain_community.chat_models.openai import ChatOpenAI
from langchain_community.llms.anthropic import Anthropic

from langchain_core.messages import BaseMessage
from typing import Annotated
from langgraph.graph import START, END, add_messages
from config import settings, get_settings


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
        self.fallback_llm = Anthropic(
            name="fallback_model",

        )
