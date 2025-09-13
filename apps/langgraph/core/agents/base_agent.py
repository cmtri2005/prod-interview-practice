from abc import ABC
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Callable


class BaseAgent(ABC):
    def __init__(self, agent_name: str, llm: BaseChatModel, tools: list[Callable]):
        super().__init__()
        self.agent_name = agent_name
        self.llm = BaseChatModel
        self.tools = tools
