from apps.langgraph.schema.jd import JD
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessages
from typing import Annotated, TypedDict, Sequence


class AgentState(TypedDict):
    jd_path: str
    jd: JD
    messages: Annotated[Sequence[BaseMessages], add_messages]
