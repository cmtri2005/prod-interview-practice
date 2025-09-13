
from fastapi import File
from apps.langgraph.schema.jd import JD
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import  TypedDict
from apps.langgraph.schema.learning_progress import LearningProgress, Module, Topic

class AgentState(TypedDict):
    jd_text : str = None
    jd: JD
    learningProgress: LearningProgress
    awaiting_input: bool = True
    idx_module: int = None
    idx_topic: int = None
    messages: list = None
    
