from typing import Callable, Dict
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from pathlib import Path
from apps.langgraph.schema.learning_progress import LearningProgress, Module, Topic
from langchain_tavily import TavilySearch 
from apps.helper.logger import LoggerSingleton
from pathlib import Path
import tempfile
from fastapi import UploadFile
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
    def select_module_node(learningProgress):
        modules = learningProgress.modules
        return {
            "require_user_input": True,
            "prompt": f"Please select one module by index (0..{len(modules)-1}):",
            "modules": [m.model_dump() for m in modules]
        }

    
    @staticmethod
    def select_topic_node(module: Module) -> Topic:
        topics = module.topics
        while True:
            raw = input("Select topic index (or 'q' to abort): ").strip()
            if raw.lower() in ("q", "quit", "exit"):
                raise KeyboardInterrupt("User aborted selection")
            if not raw.isdigit():
                print("Please enter a number.")
                continue
            idx = int(raw)
            if 0 <= idx < 7:
                break
            print("Index out of range. Try again.")

        topic_selected = topics[idx]
        return topic_selected

def default_tools_mapping() -> Dict[str, Callable]:
    
    return {
        "file_loader": Tools.file_loader,
        "input_module_selector": Tools.select_module_node,
        "input_topic_selector": Tools.select_topic_node,
        "save_raw_output": Tools.save_raw_output,
        "web_search": Tools.web_search_tavily,
    }

