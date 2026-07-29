import os.path
import uuid
from os.path import exists
from pathlib import Path

import magic
from fastapi import APIRouter

BASE_DIR = Path(__file__).parent.parent
DOCUMENT_DIR = BASE_DIR / "documents"
ACCEPTED_MIME={
    "application/pdf":".pdf",
    "application/msword":".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":".xlsx"
}



def process_document(content : bytes) -> str | None:
    chunk = content[:2048]
    mime_type = magic.from_buffer(chunk, mime=True)
    extension = None
    for mime in ACCEPTED_MIME:
        if mime == mime_type:
            extension = ACCEPTED_MIME[mime]
    if extension is None:
        return None
    unique_name = str(uuid.uuid4().hex)
    filename = f"{unique_name}{extension}"

    file_path = os.path.join(DOCUMENT_DIR,filename)
    os.makedirs(DOCUMENT_DIR,exist_ok=True)

    with open(file_path,"wb") as file:
        file.write(content)
        file.close()

    return file_path

def delete_document_from_disk(document_name: str) -> None:
    if document_name is None:
        return
    document_path = DOCUMENT_DIR / document_name
    if document_path.exists():
        document_path.unlink()











