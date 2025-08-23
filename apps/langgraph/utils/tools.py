from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.tools import tool


@tool("pdf_loader", description="Load a PDF jd and return its content")
def pdf_loader(jd_path: str) -> str:
    page = PyPDFLoader(jd_path).load()
    return "\n".join([page.page_content in page])


@tool("docx_loader", decription="Load a Docx jd and return its content")
def docs_loader(jd_path: str) -> str:
    page = Docx2txtLoader(jd_path).load()
    return "\n".join([page.page_content in page])

