import docx2txt
import fitz
from fastapi import UploadFile
import os, uuid

def extract_text_from_file(uploaded_file: UploadFile) -> str:
    if not uploaded_file.filename:
        raise ValueError("Uploaded file must have a filename")

    suffix = uploaded_file.filename.split(".")[-1].lower()
    file_bytes = uploaded_file.file.read()

    tmp_path = f"/tmp/{uuid.uuid4()}_{uploaded_file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    text = ""
    try:
        if suffix == "txt":
            text = file_bytes.decode("utf-8", errors="ignore")
        elif suffix == "docx":
            text = docx2txt.process(tmp_path)
        elif suffix == "pdf":
            with fitz.open(tmp_path) as doc:
                for page in doc:
                    text += page.get_text()
        else:
            raise ValueError("Unsupported file type")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return text


if __name__ == "__main__":
    extract_text_from_file()


