import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Literal

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer, joinedload

import models
from config import settings
from schemas import ChatResponse, ChatSource, ChatTurn
from utils.documents_utils import ACCEPTED_MIME
from utils.image_utils import create_presigned_url

collection_name = "document_chunks"

openai_client = AsyncOpenAI(api_key=settings.openai_key)


# TODO : Integrate own Document Loader with pypdf







@contextmanager
def generate_temp_file(file_bytes: bytes, extension: str):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    try:
        tmp.write(file_bytes)
        tmp.flush()
        tmp.close()
        yield tmp.name
    finally:
        os.unlink(tmp.name)


@dataclass
class DocumentLoader:
    extension: Literal[".pdf", ".doc", ".docx", ".xlsx"]
    file_bytes: bytes

    def load_document(self) -> list[Document] | None:
        match self.extension:
            case ".pdf":
                with generate_temp_file(
                    file_bytes=self.file_bytes, extension=self.extension
                ) as tmp_file:
                    loader = PyPDFLoader(file_path=tmp_file)
                    return loader.load()

            case ".doc" | ".docx":
                with generate_temp_file(
                    file_bytes=self.file_bytes, extension=self.extension
                ) as tmp_file:
                    loader = UnstructuredWordDocumentLoader(
                        file_path=tmp_file, mode="single"
                    )
                    return loader.load()

            case ".xlsx":
                with generate_temp_file(
                    file_bytes=self.file_bytes, extension=self.extension
                ) as tmp_file:
                    loader = UnstructuredExcelLoader(file_path=tmp_file, mode="single")
                    return loader.load()

            case _:
                raise ValueError(f"Extension {self.extension} is unsupported.")


@dataclass
class Processor:
    chunk_size: int
    overlap: int

    def __repr__(self) -> str:
        return f"Processor(chunk_size={self.chunk_size!r}, overlap={self.overlap})"

    def __str__(self) -> str:
        return "Base class for document type processing system. Use as blueprint for other classes."


@dataclass
class ReportProcessor(Processor):
    chunk_size: int = 300
    overlap: int = 20

    def recursive_chunking(self, documents):
        """Text splitter used for returning chunks split with Recursive chunking algorithm. Input: Document Returns: the processed chunks."""
        if not documents:
            raise ValueError("No documents to process.")
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_documents(documents)

        print(f"Original length: {len(documents)} chars")
        print(f"Number of chunks: {len(chunks)}")
        return chunks

    def __str__(self) -> str:
        return "Report processor used for chunking and processing report document type."


async def embedd(chunks):
    """

     Embed each document using OPENAI text-embedding-3-small.
     Return provided embeddings for database save.

    """
    client = AsyncOpenAI(api_key=settings.openai_key)
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=[c.page_content for c in chunks]
    )
    return [v.embedding for v in response.data]

def to_human_page(page:int | None) -> int | None:
    """PyPDFLoader numbers pages from 0; store them 1-based so citations match the PDF viewer."""
    return page + 1 if page is not None else None

async def save_embeddings(
    db,
    chunks,
    embeddings,
    document_id: int,
    client_id: int,
):
    rows = [
        models.DocumentChunk(
            document_id=document_id,
            client_id=client_id,
            text=chunk.page_content,
            embedding=vector,
            chunk_index=index,
            page=to_human_page(chunk.metadata.get("page")),
        )
        for index, (chunk, vector) in enumerate(zip(chunks, embeddings))
    ]

    db.add_all(rows)


async def retrieve_chunks(
    db: AsyncSession, query: str, client_id: int, top_k: int = 3
) -> list[models.DocumentChunk]:
    client = AsyncOpenAI(api_key=settings.openai_key)
    response = await client.embeddings.create(
        model="text-embedding-3-small", input=query
    )
    query_embedding = response.data[0].embedding

    stmt = (
        select(models.DocumentChunk)
        .options(
            # many-to-one : a single JOIN, no row multiplication
            joinedload(models.DocumentChunk.document),
            defer(models.DocumentChunk.embedding),
        )
        .where(models.DocumentChunk.client_id == client_id)
        .order_by(models.DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
    )

    content = await db.execute(stmt)
    content = content.scalars().all()

    return list(content)


SYSTEM_PROMPT = """You are a document assistant that answers questions about a specific client's documents.

Your rules:
- Answer EXCLUSIVELY based on the context provided below. The context consists of excerpts retrieved from the client's documents.
- If the answer is not contained in the context, say clearly that the information is not available in the documents. Do not guess, and do not use outside knowledge to fill gaps.
- Do not invent facts, figures, dates, or names that are not present in the context.
- When you state a fact, cite its source using the document title and page given in the header of each excerpt (e.g. "according to Annual report 2024, page 2").
- If the context contains conflicting information, point out the conflict rather than choosing one silently.
- Keep answers concise and grounded in the text. Quote short phrases from the context when precision matters.
- Answer in the same language as the user's question."""

NO_CONTEXT_ANSWER = (
    "I couldn't find anything relevant to this question in this client's documents."
)


def format_context(chunks: list[models.DocumentChunk]) -> str:
    parts = []
    for chunk in chunks:
        page = chunk.page if chunk.page is not None else "n/a"
        parts.append(f'[document "{chunk.document.name}", page {page}]\n{chunk.text}')
    return "\n\n".join(parts)


EXTENSION_TO_MIME = {ext: mime for mime, ext in ACCEPTED_MIME.items()}
# If the document type is not found in ACCEPTED_MIME
FALLBACK_MIME = "application/octet-stream"


def build_sources(chunks: list[models.DocumentChunk]) -> list[ChatSource]:
    # Several chunks can come from the same document: keep one source per
    # document, in order of first appearance (= best distance).
    sources: dict[int, ChatSource] = {}
    for chunk in chunks:
        doc = chunk.document
        if doc.id in sources:
            continue
        sources[doc.id] = ChatSource(
            id=doc.id,
            title=doc.name,
            # Create presigned url, for accessing the document from AWS S3 Bucket.
            url=create_presigned_url(
                object_name=f"files/{doc.file}",
                response_type=EXTENSION_TO_MIME.get(doc.extension_type, FALLBACK_MIME),
            ),
        )
    # Return a list of sources used to justify LLM Response based on the provided embeddings
    return list(sources.values())


async def generate_answer(
    db: AsyncSession,
    query: str,
    client_id: int,
    history: list[ChatTurn] | None = None,
    top_k: int = 5,
) -> ChatResponse:
    """

    Function used to generate an answer back into the endpoint.
    This function takes a query, a history of conversation and provide the right answer back the endpoint.

    """
    # Retrieve the chunks specifying the user query and client_id, ensuring data protection

    chunks = await retrieve_chunks(db=db, query=query, client_id=client_id, top_k=top_k)
    if not chunks:
        return ChatResponse(answer=NO_CONTEXT_ANSWER)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        # Earlier turns come from the browser: untrusted, already length-capped by ChatRequest.
        *({"role": t.role, "content": t.content} for t in (history or [])),
        {
            "role": "user",
            "content": f"Context:\n{format_context(chunks)}\n\nQuery: {query}",
        },
    ]

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )

    return ChatResponse(
        answer=response.choices[0].message.content or NO_CONTEXT_ANSWER,
        sources=build_sources(chunks),
    )
