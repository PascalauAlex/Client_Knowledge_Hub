import uuid
from pathlib import Path
import magic
from io import BytesIO

BASE_DIR = Path(__file__).parent.parent
DOCUMENT_DIR = BASE_DIR / "documents"
ACCEPTED_MIME={
    "application/pdf":".pdf",
    "application/msword":".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":".xlsx"
}



def process_document(content : bytes) -> tuple[bytes,str, str | None] | None:
    chunk = content[:2048]
    mime_type = magic.from_buffer(chunk, mime=True)
    extension = None
    for mime in ACCEPTED_MIME:
        if mime == mime_type:
            extension = ACCEPTED_MIME[mime]
    if extension is None:
        extension = None
    unique_name = str(uuid.uuid4().hex)
    filename = f"{unique_name}{extension}"

    output = BytesIO(content)
    output.seek(0)

    return output.read() ,filename, extension

def delete_document_from_disk(document_name: str) -> None:
    if document_name is None:
        return
    document_path = DOCUMENT_DIR / document_name
    if document_path.exists():
        document_path.unlink()














