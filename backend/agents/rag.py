import os
import tempfile
from dataclasses import dataclass
from typing import Literal
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config import settings
from langchain_core.documents import Document
import models
from openai import AsyncOpenAI
import tiktoken

collection_name = "document_chunks"


@dataclass
class DocumentLoader:
    extension: Literal[".pdf", ".doc", ".docx", ".xlsx"]
    file_bytes : bytes

    def load_document(self) -> list[Document] | None:
        match self.extension:
            case ".pdf":
                tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=self.extension)
                try:
                    tmpfile.write(self.file_bytes)
                    tmpfile.flush()
                    tmpfile.close()
                    loader = PyPDFLoader(tmpfile.name)
                    return loader.load()
                finally:
                    os.unlink(tmpfile.name)

            case _:
                raise ValueError(f"Extension {self.extension} is unsupported.")



@dataclass
class Processor:
    chunk_size : int
    overlap : int

    def __repr__(self) -> str:
        return f"Processor(chunk_size={self.chunk_size}, overlap={self.overlap})"
    def __str__(self) -> str:
        return "Base class for document type processing system. Use as blueprint for other classes."


@dataclass
class ReportProcessor(Processor):
    chunk_size : int = 300
    overlap : int = 20

    def recursive_chunking(self,documents):
        if not documents:
            raise ValueError("No documents to process.")
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=["\n\n","\n"," ",""],


        )
        chunks = splitter.split_documents(documents)

        print(f"Original length: {len(documents)} chars")
        print(f"Number of chunks: {len(chunks)}")
        return chunks


async def embedd(chunks):
    client = AsyncOpenAI(api_key=settings.openai_key)
    response = await client.embeddings.create(model="text-embedding-3-small",input=[c.page_content for c in chunks])
    return [v.embedding for v in response.data]


async def save_embeddings(db,
                          chunks,
                          embeddings,
                          document_id : int,
                          client_id : int,
                          ):
    rows = [
        models.DocumentChunk(
            document_id=document_id,
            client_id=client_id,
            text=chunk.page_content,
            embedding=vector,
            chunk_index=index,
            page=chunk.metadata.get("page")
        )
        for index,(chunk , vector) in enumerate(zip(chunks,embeddings))
    ]

    db.add_all(rows)




















