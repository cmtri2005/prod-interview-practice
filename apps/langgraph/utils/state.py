from typing import TypedDict
from apps.langgraph.schema.jd import JD
from apps.langgraph.schema.learning_progress import LearningProgress


class AgentState(TypedDict):
    jd_text: str = None
    jd: JD
    learningProgress: LearningProgress
    idx_module: int = None
    idx_topic: int = None
    messages: list = None
    next_agent: str = None
    exit_graph: bool = None
    thread_id: str = None
