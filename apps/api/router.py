import uuid
from fastapi import UploadFile, File, APIRouter
from pydantic import BaseModel
from apps.langgraph.core.agents.orchestrator import Orchestrator
from langgraph.checkpoint.memory import InMemorySaver
from apps.helper.logger import LoggerSingleton
from apps.langgraph.utils.tools import Tools
logger = LoggerSingleton().get_instance()


router = APIRouter()
orchestrator = Orchestrator(checkpointer=InMemorySaver())
lang_app = orchestrator.build_graph()

class PathIn(BaseModel):
    jd_path: str

class Input_Module(BaseModel):
    thread_id: str
    idx_module: int
    
    
@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    thread_id = str(uuid.uuid4())
    events = []
    text = ""
    
    
    try:
        logger.info(f"Loading JD from: {file.filename}")
        jd_content = await Tools.file_loader(file)
    except Exception as e:
        logger.error(f"Error: {e}")
        raise ValueError(f"Failed to load JD file: {e}")

    try:
        async for ev in lang_app.astream(
            {"jd_text": jd_content},
            config={"configurable": {"thread_id": thread_id}}
        ):
            events.append(ev)
            
            if "Analyze_modules_Agent" in ev and ev["Analyze_modules_Agent"].get("awaiting_input"):
                logger.info("Graph signaled awaiting_input -> breaking astream to return to client")
                break

    except Exception as e:
        logger.exception("Error while running graph:", e)
        raise
    
    output = {
        "Extract JD Agent": events[0]["JD_extract"].get("jd"),
        "Learning Progress Agent": events[1]["Learning_Progress_Agent"].get("learningProgress"),
        # "messages": events[-1]["Analyze_modules_Agent"].get("messages"),
        "thread_id": thread_id
    }
    return output



@router.post("/input_module")
async def input_module(idx: Input_Module):
    events = []
    async for ev in lang_app.astream(
        {"idx_module": idx.idx_module},
        config={"configurable": {"thread_id": idx.thread_id}}
    ):
        events.append(ev)
    return {"Analysis Agent": events[-1]["Analyze_modules_Agent"].get("messages")}




