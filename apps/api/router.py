import uuid
from fastapi import UploadFile, File, APIRouter
from pydantic import BaseModel
from apps.langgraph.core.agents.orchestrator import Orchestrator
from langgraph.checkpoint.memory import InMemorySaver
from apps.helper.logger import LoggerSingleton
from apps.langgraph.utils.tools import Tools
from apps.langgraph.core.agents.generate_quiz_agent import GenQuizAgent
from apps.langgraph.core.agents.generate_quiz_agent import get_model
from apps.langgraph.schema.interview_quiz import QuizOut
from typing import List
logger = LoggerSingleton().get_instance()


router = APIRouter()
orchestrator = Orchestrator(checkpointer=InMemorySaver())
lang_app = orchestrator.build_graph()


class PathIn(BaseModel):
    jd_path: str


class Input_Module(BaseModel):
    thread_id: str
    idx_module: int


@router.post("/gen_learning_progress")
async def gen_learning_progress(file: UploadFile = File(...)):
    thread_id = str(uuid.uuid4())
    events = []

    try:
        logger.info(f"Loading JD from: {file.filename}")
        jd_content = await Tools.file_loader(file)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Failed to load JD file: {e}")

    try:
        async for ev in lang_app.astream(
            {"jd_text": jd_content, "next_agent": "JD_Extract"},
            config={"configurable": {"thread_id": thread_id}},
        ):
            events.append(ev)
            if len(events) == 3:
                break

    except Exception as e:
        logger.exception("Error while running graph:", e)
        raise

    output = {
        "messages": events[-1]["Analyze_Modules_Agent"].get("messages"),
        "thread_id": thread_id,
    }
    return output


@router.post("/input_module")
async def input_module(idx: Input_Module):
    events = []
    async for ev in lang_app.astream(
        {"idx_module": idx.idx_module, "next_agent": "Analyze_Modules_Agent"},
        config={"configurable": {"thread_id": idx.thread_id}},
    ):
        events.append(ev)
    return {"messages": events[0]["Analyze_Modules_Agent"].get("messages")}


@router.post("/exit_graph")
async def input_module(thread_id: str):
    events = []
    async for ev in lang_app.astream(
        {
            "exit_graph": True,
            "thread_id": thread_id,
            "next_agent": "Analyze_Modules_Agent",
        },
        config={"configurable": {"thread_id": thread_id}},
    ):
        events.append(ev)
    return {"messages": events[0]["Analyze_Modules_Agent"].get("messages")[-1]}


@router.post("/load_history")
async def load_history(thread_id: str):
    events = []
    async for ev in lang_app.astream(
        {"thread_id": thread_id, "next_agent": "Analyze_Modules_Agent"},
        config={"configurable": {"thread_id": thread_id}},
    ):
        events.append(ev)
    return {"messages": events[0]["Analyze_Modules_Agent"].get("learningProgress")}


@router.post("/generate_quiz")
async def generate_quiz(user_id: str, topic: str, difficulty: str) -> QuizOut:
    try:
        logger.info("/generate_quiz")
        llm = get_model()
        agent = GenQuizAgent("Gen Quiz Agent", llm, None)
        quiz = agent.generate_quiz(user_id, topic, difficulty)
        return quiz
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise ValueError(f"Failed to generate quiz: {e}")


@router.post("/answer_quiz")
async def answer_quiz(user_id: str, quiz_id: str, answer: str) -> QuizOut:
    try:
        logger.info("/answer_quiz")
        llm = get_model()
        agent = GenQuizAgent("Gen Quiz Agent", llm, None)
        quiz = agent.handle_answer_quiz(user_id, quiz_id, answer)
        return quiz
    except Exception as e:
        logger.error(f"Error answering quiz: {e}")
        raise ValueError(f"Failed to answer quiz: {e}")
