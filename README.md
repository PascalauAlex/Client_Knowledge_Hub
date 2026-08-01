# Client Knowledge Hub 🧠💼

A standalone microservice built with **FastAPI** designed to aggregate, manage, and query unstructured client data (meeting notes, emails, feedback, tickets). 

While traditional CRMs handle structured data, this service acts as the **narrative memory** for a client and serves as the foundational ingestion layer for a **Retrieval-Augmented Generation (RAG)** AI Assistant.

## 🚀 Key Features

- **Decoupled Architecture:** Integrates seamlessly with any existing CRM using `external_crm_id` mapping.
- **Narrative CRUD:** Complete management of Clients and nested Documents categorized by `source_type`.
- **Dual-Strategy Authentication:**
  - **JWT (JSON Web Tokens):** For human users (e.g., sales reps) accessing the system via a frontend client.
  - **API Keys (M2M):** For secure machine-to-machine communication, allowing external CRMs to push/pull data.
- **RAG-Ready Foundation:** Designed to be easily extended with `pgvector` to support semantic search and LLM-powered queries over client histories.

## 🤖 AI-Powered RAG Pipeline (The "Brain")

The core value of this system goes beyond file storage; it transforms static text into an interactive, agentic assistant. The upcoming AI architecture implements a complete Data Engineering and Retrieval-Augmented Generation pipeline:

- **Automated Ingestion & Chunking:** Asynchronously processes unstructured documents (PDFs, DOCX, etc.), splitting large texts into semantic, manageable chunks.
- **Vector Embeddings:** Transforms text chunks into high-dimensional vector representations using embedding models (e.g., OpenAI `text-embedding-3-small`).
- **Native Vector Storage:** Leverages PostgreSQL with the **`pgvector`** extension for highly efficient, local similarity search, keeping tabular data and vector data in a unified database.
- **Semantic Retrieval (`/clients/{id}/ask`):** An endpoint where users can ask natural language questions (e.g., *"What discount did we promise this client last month?"*). The system performs a semantic search to retrieve the most relevant historical context.
- **Grounded LLM Synthesis:** The retrieved context is fed to an LLM to generate a precise, factual answer, strictly grounded in the client's actual data, complete with citations linking back to the original source documents.

## 🛠️ Tech Stack

- **Frameworks:** FastAPI (Python), React (TypeScript)
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Authentication:** JWT 
- **Future AI Integration:** `pgvector`, LangChain/OpenAI (Planned)

### ☁️ Storage & Document Management
- **Multi-Format Support:** Users can seamlessly upload and manage diverse file types, including `.pdf`, `.doc`, `.docx`, `.xlsx`, and `.csv`.
- **Safe file upload:** The documents are verified and checked by MIME type before uploading.
- **AWS S3 Integration:** All documents and attachments are securely stored in the cloud using Amazon S3 buckets, ensuring high availability, scalability, and decoupled file management.
- **AWS Presigned URLs:** Only the authenticated owner of the client can see and interact with the documents, through a secured presigned URL provided by the AWS SDK (boto3).

### 🔐 Security & Account Management
- **Password Recovery:** Built-in secure password reset flow. Users can request a password reset, which triggers an email containing a secure, time-limited recovery token.

### 🧪 Reliability
- **Endpoint Testing:** Comprehensive test coverage across all REST API endpoints (using **`pytest`** and **`httpx`**) to ensure data integrity, validate authentication flows, and prevent regressions during continuous development.

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/PascalauAlex/Client_Knowledge_Hub.git](https://github.com/PascalauAlex/Client_Knowledge_Hub.git)
   cd Client_Knowledge_Hub
