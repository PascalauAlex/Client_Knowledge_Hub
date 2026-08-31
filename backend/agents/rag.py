import tempfile
from typing import Literal
from typing import Annotated
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_postgres import PGVector
from mpmath.ctx_iv import convert_mpf_
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from config import settings
from langchain_core.documents import Document

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
connection = settings.database_url
collection_name = "document_chunks"



class DocumentLoader(BaseModel):
    extension: Literal[".pdf", ".doc", ".docx", ".xlsx"]
    file_bytes : bytes

    def load_document(self) -> list[Document] | None:
        match self.extension:
            case ".pdf":
                with tempfile.NamedTemporaryFile(delete=True, suffix=self.extension) as tmpfile:
                    tmpfile.write(self.file_bytes)
                    tmpfile.flush() # Write on disk

                    loader = PyPDFLoader(tmpfile.name)
                    documents = loader.load()
                    return documents
            case _:
                return None


def create_vectorstore():
    return PGVector(
        embeddings=embeddings,
        connection=connection,
        collection_name=collection_name,
        use_jsonb=True
    )






