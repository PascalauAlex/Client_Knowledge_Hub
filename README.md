Client Knowledge Hub 🧠💼

A standalone microservice built with FastAPI designed to aggregate, manage, and query unstructured client data (meeting notes, emails, feedback, tickets).

While traditional CRMs handle structured data, this service acts as the narrative memory for a client and serves as the foundational ingestion layer for advanced AI integrations.
🚀 Key Features

    Decoupled Architecture: Integrates seamlessly with any existing CRM using external_crm_id mapping.

    Narrative CRUD: Complete management of Clients and nested Documents categorized by source_type.

    Dual-Strategy Authentication:

        JWT (JSON Web Tokens): For human users (e.g., sales reps) accessing the system via a frontend client.

        API Keys (M2M): For secure machine-to-machine communication, allowing external CRMs to push/pull data.

    RAG-Ready Foundation: Designed to be easily extended with pgvector to support semantic search and LLM-powered queries over client histories.

🤖 AI Capabilities: Agentic Extraction & Future RAG

The core value of this system goes beyond file storage; it transforms static text into structured, actionable insights.
🟢 Currently Implemented: Agentic Structured Extraction

Before jumping into open-ended chat (RAG), the system employs LlamaIndex and LlamaCloud Extract to intelligently summarize and parse unstructured files:

    Structured Invoice Parsing: Uploaded invoices (PDFs, images) are passed through an agentic extraction pipeline that reads the unstructured document and returns strictly typed JSON data (Vendor, Invoice Date, Due Date, Items, Total) validated via Pydantic schemas.

    Automated Document Summaries: Generates concise, structured summaries of complex client documents, turning lengthy PDFs into scannable insights without requiring a human to read them end-to-end.

🟡 Planned Milestone: The RAG Pipeline (The "Brain")

The ultimate goal of this architecture is to implement a complete Retrieval-Augmented Generation pipeline:

    Automated Ingestion & Chunking: Asynchronously splitting large texts into semantic, manageable chunks.

    Native Vector Storage: Leveraging PostgreSQL with the pgvector extension for highly efficient, local similarity search.

    Semantic Retrieval (/clients/{id}/ask): An endpoint where users can ask natural language questions (e.g., "What discount did we promise this client last month?").

    Grounded LLM Synthesis: Generating precise, factual answers strictly grounded in the client's actual data, complete with citations linking back to the original source documents.

🛠️ Tech Stack

    Frameworks: FastAPI (Python), React (TypeScript)

    Database: PostgreSQL (with SQLAlchemy ORM)

    AI & Data Extraction: LlamaIndex, LlamaCloud (Agentic Extraction)

    Authentication: JWT

    Future AI Integration: pgvector, LangChain/OpenAI (Planned)

☁️ Storage & Document Management

    Multi-Format Support: Users can seamlessly upload and manage diverse file types, including .pdf, .doc, .docx, .xlsx, and .csv.

    Safe File Upload: Documents are verified and checked by MIME type before uploading.

    AWS S3 Integration: All documents and attachments are securely stored in the cloud using Amazon S3 buckets, ensuring high availability, scalability, and decoupled file management.

    AWS Presigned URLs: Only the authenticated owner of the client can see and interact with the documents, through a secured presigned URL provided by the AWS SDK (boto3).

🔐 Security & Reliability

    Password Recovery: Built-in secure password reset flow. Users can request a password reset, which triggers an email containing a secure, time-limited recovery token.

    Endpoint Testing: Comprehensive test coverage across all REST API endpoints (using pytest and httpx) to ensure data integrity, validate authentication flows, and prevent regressions during continuous development.

🚦 Getting Started
Prerequisites

    Python 3.10+

    PostgreSQL

    AWS S3 Credentials (for file storage)

    LlamaCloud API Key (for document extraction)

Installation

Clone the repository:
Bash

git clone https://github.com/PascalauAlex/Client_Knowledge_Hub.git
cd Client_Knowledge_Hub
