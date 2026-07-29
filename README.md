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

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (with SQLAlchemy ORM)
- **Authentication:** JWT 
- **Future AI Integration:** `pgvector`, LangChain/OpenAI (Planned)

### ☁️ Storage & Document Management
- **Multi-Format Support:** Users can seamlessly upload and manage diverse file types, including `.pdf`, `.doc`, `.docx`, `.xlsx`, and `.csv`.
- **AWS S3 Integration:** All documents and attachments are securely stored in the cloud using Amazon S3 buckets, ensuring high availability, scalability, and decoupled file management.

### 🔐 Security & Account Management
- **Password Recovery:** Built-in secure password reset flow. Users can request a password reset, which triggers an email containing a secure, time-limited recovery token.

### 🧪 Reliability
- **Endpoint Testing:** Comprehensive test coverage across all REST API endpoints (using `pytest` and `httpx`) to ensure data integrity, validate authentication flows, and prevent regressions during continuous development.

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL

### Installation
1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/PascalauAlex/Client_Knowledge_Hub.git
   cd Client_Knowledge_Hub
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   \`\`\`

3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. Set up your `.env` file (Database URL, JWT Secret Key, etc.).

5. Run the application:
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`
   Access the interactive API documentation at `http://localhost:8000/docs`.
