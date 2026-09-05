import os
import tempfile
from dataclasses import dataclass
from typing import Literal
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from langchain_core.documents import Document
import models
from openai import AsyncOpenAI
import tiktoken
from sqlalchemy import select

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


async def retrieve_chunks(
        db:AsyncSession,
        query:str,
        client_id:int,
        top_k : int = 3
)->list[models.DocumentChunk]:
    client = AsyncOpenAI(api_key=settings.openai_key)
    response = await client.embeddings.create(model="text-embedding-3-small",
                                              input=query)
    query_embedding = response.data[0].embedding

    stmt = (
        select(models.DocumentChunk)
        .where(models.DocumentChunk.client_id == client_id)
        .order_by(models.DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


SYSTEM_PROMPT = """You are a document assistant that answers questions about a specific client's documents.

Your rules:
- Answer EXCLUSIVELY based on the context provided below. The context consists of excerpts retrieved from the client's documents.
- If the answer is not contained in the context, say clearly that the information is not available in the documents. Do not guess, and do not use outside knowledge to fill gaps.
- Do not invent facts, figures, dates, or names that are not present in the context.
- When you state a fact, cite its source using the document and page provided with each excerpt (e.g. "according to document 16, page 2").
- If the context contains conflicting information, point out the conflict rather than choosing one silently.
- Keep answers concise and grounded in the text. Quote short phrases from the context when precision matters.
- Answer in the same language as the user's question."""

async def generate_answer(db, query: str, client_id: int, top_k: int = 5) -> str:
    chunks = await retrieve_chunks(db=db, query=query, client_id=client_id, top_k=top_k)
    if not chunks:
        return "The's no answer for this query!"

    context = "\n\n".join(
        f"[document {c.document_id}, page {c.page}]\n{c.text}" for c in chunks
    )

    client = AsyncOpenAI(api_key=settings.openai_key)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content




















