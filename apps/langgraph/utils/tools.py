from typing import Callable, Dict
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from pathlib import Path
from apps.langgraph.schema.learning_progress import LearningProgress
from apps.langgraph.schema.jd import JD
from langchain_tavily import TavilySearch 
from apps.helper.logger import LoggerSingleton
from pathlib import Path
import tempfile
from fastapi import UploadFile
from apps.chroma_db.postgres.db_agent import SessionLocal
from apps.chroma_db.postgres.dao import JDDAO, LearningProgressDAO, MessageDAO
from apps.langgraph.utils.state import AgentState
import json
logger = LoggerSingleton().get_instance()

class Tools:
    @staticmethod
    async def file_loader(file: UploadFile) -> str:
        suffix = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        # chọn loader theo extension
        if suffix == ".txt":
            loader = TextLoader(str(tmp_path), encoding="utf-8")
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(tmp_path))
        elif suffix == ".pdf":
            loader = PyPDFLoader(str(tmp_path))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        docs = loader.load()
        return "\n".join(d.page_content for d in docs)

    

    @staticmethod
    def save_raw_output(fname: str, content: str):
        try:
            p = Path("/mnt/d/Desktop/Desktop/MLOps/prod-interview-practice/apps/langgraph/outputs")
            p.mkdir(parents=True, exist_ok=True)
            path = p / fname
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(e)

 
    @staticmethod
    def web_search_tavily():
        return TavilySearch(max_results=4)
    
    
    @staticmethod
    def save_agent_state(state: AgentState, thread_id: str):
        
        db = SessionLocal()
        try:
            id = thread_id
            
            jd_dao = JDDAO(db)
            jd = state.get("jd").model_dump_json()
            jd_text = state.get("jd_text")
            jd_dao.insert(id, jd_text, jd)

            lp_dao = LearningProgressDAO(db)
            lp = state.get("learningProgress").model_dump_json()
            lp_dao.insert(id, lp)

            msg_dao = MessageDAO(db)
            msg = json.dumps(state.get("messages"))
            msg_dao.insert(id, msg)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

def default_tools_mapping() -> Dict[str, Callable]:
    
    return {
        "file_loader": Tools.file_loader,
        "save_raw_output": Tools.save_raw_output,
        "web_search": Tools.web_search_tavily,
        "save_state": Tools.save_agent_state
    }

