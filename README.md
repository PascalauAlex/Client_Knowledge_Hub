# Client Knowledge Hub 🧠💼

A standalone microservice built with **FastAPI**, designed to aggregate, manage, and query client data (invoices, reports, contracts).

While traditional CRMs handle structured data, this service acts as the **narrative memory** for a client and serves as the foundational ingestion layer for advanced AI integrations.

---

## 🚀 Key Features

- **Decoupled Architecture:** Integrates with any existing CRM using `external_crm_id` mapping.
- **Narrative CRUD:** Complete management of Clients and nested Documents categorized by type.
- **JWT Authentication:** For human users (e.g., sales reps) accessing the system via a frontend client.

---

## 🤖 RAG Pipeline — Retrieval-Augmented Generation

The core value of this system goes beyond file storage: it turns a client's documents into a **searchable, queryable knowledge base** that answers natural-language questions grounded in the client's own data.

The pipeline is built **natively on PostgreSQL + pgvector** — embeddings, metadata, and similarity search all live in the application's own schema, under real foreign keys and per-client isolation. No external vector store or vector-DB abstraction is used; the service owns the full path from bytes to answer.

### Architecture

The RAG flow is split into a clear ingestion path and a retrieval path.

**Ingestion (on document upload):**

1. **Load** — The raw file bytes are parsed into text. PDFs are handled via `PyPDFLoader`, preserving per-page metadata for later citations.
2. **Chunk** — Text is split into overlapping, token-sized chunks using a `RecursiveCharacterTextSplitter` configured with a **tiktoken** encoder, so `chunk_size` and `overlap` are measured in tokens rather than characters. Chunking strategy is selected **per document type** (currently `report`).
3. **Embed** — Each chunk is embedded with OpenAI `text-embedding-3-small` (1536-dim) in a single batched, asynchronous call.
4. **Store** — Chunks are persisted to the `document_chunks` table, each row carrying its vector plus full provenance: `document_id`, `client_id`, `chunk_index`, and `page`.

**Retrieval (on query):**

1. **Authorize** — The requesting user's ownership of the target client is verified *before* any retrieval, so the client scope is derived from authorization, never from a caller-supplied parameter.
2. **Embed the question** — The natural-language query is embedded with the same model used at ingestion, keeping question and chunks in one vector space.
3. **Similarity search** — Nearest chunks are found with pgvector's `cosine_distance`, **filtered by `client_id`** in the same query. This `WHERE client_id = ...` on a real, indexed column is the system's security boundary: a user can never retrieve another client's chunks.
4. **Grounded synthesis** *(in progress)* — Retrieved chunks are packed into an LLM prompt with strict instructions to answer **only** from the provided context and to cite the source document and page.

### Design decisions worth noting

- **Native schema ownership over a vector-store abstraction.** Storing vectors in the app's own `document_chunks` table (rather than a managed vector store) means deleting a document cascades to its chunks at the database level, and client isolation is a plain column filter — simple to reason about and hard to get wrong.
- **Per-client isolation as a first-class security concern.** `client_id` is denormalized onto every chunk and enforced both by the query filter and by authorization upstream.
- **Provenance for citations.** `chunk_index` and `page` are carried through the whole pipeline so answers can point back to exactly where a fact came from.
- **Atomic ingestion.** Document row and its chunks are written in a single all-or-nothing transaction; any failure (parsing, embedding, DB) triggers a rollback and cleans up the already-uploaded S3 object, so the system never ends up with a "mute" document that exists but has no searchable context.

### Status

| Capability | State |
| --- | --- |
| Embedding generation for `report` documents | ✅ Implemented |
| Vector storage in PostgreSQL via pgvector | ✅ Implemented |
| Atomic upload with rollback + S3 cleanup | ✅ Implemented |
| Semantic retrieval, client-isolated (`cosine_distance`) | ✅ Implemented |
| Grounded LLM synthesis with citations | 🟡 In progress |
| Additional document types (`contract`) & structured invoice handling | 🔜 Planned |
| Approximate vector index (HNSW) for scale | 🔜 Planned |

---

## 🧾 Agentic Structured Extraction

Alongside RAG, the system parses unstructured files into typed data using **LlamaIndex** and **LlamaCloud Extract**:

- **Structured Invoice Parsing:** Uploaded invoices (PDFs, images) run through an agentic extraction pipeline that returns strictly typed JSON (Vendor, Invoice Date, Due Date, Items, Total), validated via **Pydantic** schemas.
- **Automated Document Summaries:** Generates concise, structured summaries of complex client documents, turning lengthy PDFs into scannable insights.

> **Note:** Invoices are handled by structured extraction rather than semantic RAG — their questions are typically aggregate ("what did we invoice this client in Q1?"), which structured fields answer better than similarity search.

---

## ☁️ Storage & Document Management

- **Multi-Format Support:** Upload and manage `.pdf`, `.doc`, `.docx`, `.xlsx`, and `.csv`.
- **Safe File Upload:** Documents are verified by MIME type before upload.
- **AWS S3 Integration:** All documents are stored in Amazon S3 for high availability and decoupled file management.
- **AWS Presigned URLs:** Only the authenticated owner of a client can access its documents, via secured presigned URLs (boto3).

---

## 🔐 Security & Reliability

- **Password Recovery:** Secure, time-limited token-based password reset flow delivered by email.
- **Endpoint Testing:** Test coverage across REST endpoints (pytest + httpx) to validate auth flows and prevent regressions.

---

## 🛠️ Tech Stack

- **Frameworks:** FastAPI (Python), React (TypeScript)
- **Database:** PostgreSQL (SQLAlchemy ORM, async) + pgvector for the embedding store
- **RAG:** pgvector similarity search, OpenAI `text-embedding-3-small`, LangChain text splitters (tiktoken)
- **Structured Extraction:** LlamaIndex, LlamaCloud
- **Authentication:** JWT
- **Monitoring:** LangSmith

---

## 🚦 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL with the pgvector extension (preferably as a 🐋 Docker image)
- AWS S3 credentials (for file storage)
- OpenAI API key (for embeddings and synthesis)
- LlamaCloud API key (for structured extraction)

### Installation

```bash
git clone https://github.com/PascalauAlex/Client_Knowledge_Hub.git
cd Client_Knowledge_Hub
```
