# Compliance Checker (Clause-Level)  
### FastAPI + LangChain + ChromaDB + Ollama + Streamlit

---

## 1) What This Project Is About (High-Level)

This project is a **Clause-Level Compliance Checker** for legal documents.  
It compares contract clauses against a regulations/policy document and generates a detailed compliance report.

### Core Idea
- You store a **regulations / compliance rules document** (large PDF).
- The system embeds the regulations into **ChromaDB** (vector database).
- The user uploads a **contract document** (PDF/DOCX).
- The contract is converted into text, split into clauses, and each clause is checked against the most relevant regulation rules.
- The system returns:
  - Compliance status per clause (COMPLIANT / NON_COMPLIANT / NEEDS_REVIEW)
  - Rule mapping (rule → relevance → violation)
  - Risk level and impact
  - Rectification steps
  - Recommended contract changes
  - Suggested rewritten clause (compliant legal language)

This system is designed like enterprise-grade compliance tooling:  
✅ RAG pipeline (Retrieval Augmented Generation) + LLM reasoning + vector similarity search.

---

## 2) Why This Project Exists (Problem Statement)

Manual compliance checking is slow:
- a human must read 20–50 page contracts
- compare each clause with security/privacy policies
- highlight violations and suggest contract edits

This project automates that workflow with:
- **Vector retrieval** to find relevant rules
- **LLM reasoning** to produce audit-grade output
- **API + UI** for usability

---

## 3) What A Compliance Checker Does (In Practice)

A compliance checker answers questions like:
- Does the contract ensure data is encrypted at rest/in transit?
- Does it require MFA for admin accounts?
- Is retention within policy limits?
- Does it restrict sharing with third parties without consent?
- Is breach notification aligned to policy timelines?
- Does it mandate audit logs and log retention?

For each clause, the system:
1. Matches relevant policies (vector similarity search)
2. Explains compliance reasoning
3. Suggests fixes / rewritten clauses

---

## 4) System Components (Multi-file System)

This project consists of two major components:

### 4.1 Backend (FastAPI)
- Stores and retrieves vectors using ChromaDB
- Parses documents (PDF/DOCX)
- Runs compliance analysis using RAG + LLM
- Exposes APIs for Streamlit UI

### 4.2 Frontend (Streamlit UI)
- Upload regulations PDF
- Upload contract PDF/DOCX
- View compliance report in UI

---

## 5) Full Architecture (Flow)

```
User (Streamlit UI)
        |
        | Upload Regulations PDF
        v
FastAPI: /regulations/ingest
        |
        | -> PDF -> Text -> Chunk -> Embeddings
        v
ChromaDB persists regulation vectors
        |
        | Upload Contract PDF/DOCX
        v
FastAPI: /compliance/upload
        |
        | -> Parse -> Split into clauses
        | -> Retrieve matching rules (vector search)
        | -> LLM evaluates compliance
        v
Compliance Report JSON
        |
        v
Streamlit UI displays clause-by-clause audit report
```

---

## 6) Folder Structure (Explained in Detail)

Project layout:

```
compliance-checker/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── utils.py
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   ├── middlewares.py
│   │   │
│   │   ├── data/
│   │   │   ├── regulations_master.pdf
│   │   │   └── uploads/
│   │   │
│   │   ├── llm/
│   │   │   └── ollama_client.py
│   │   │
│   │   ├── services/
│   │   │   ├── file_parser.py
│   │   │   └── compliance_service.py
│   │   │
│   │   ├── vectordb/
│   │   │   ├── chroma_client.py
│   │   │   ├── retriever.py
│   │   │   └── ingest_regulations_pdf.py
│   │
│   ├── chroma_store/
│   │   └── chroma.sqlite3
│   │
│   ├── logs/
│   │   └── app.log
│   │
│   ├── tests/
│   │   ├── test_api.py
│   │   ├── test_utils.py
│   │   ├── test_file_parser.py
│   │   └── test_health.py
│   │
│   ├── requirements.txt
│   └── README.md  (optional backend-only README)
│
└── streamlit_app/
    └── app.py
```

---

## 7) What Each Important File Does

### backend/app/main.py
- FastAPI entry point
- Defines API routes:
  - `/regulations/ingest`
  - `/compliance/upload`
  - `/db/count`
- Auto-ingests regulations at startup if vector DB is empty

### backend/app/services/file_parser.py
- Extracts text from PDF and DOCX
- Handles parsing errors and returns clean text

### backend/app/utils.py
- Splits contract into clauses
- Uses numbering `1.`, `2.`, etc.
- Prevents excessive clause splitting for speed

### backend/app/vectordb/chroma_client.py
- Creates / returns ChromaDB vector store client
- Uses persistent directory `backend/chroma_store`

### backend/app/vectordb/ingest_regulations_pdf.py
- Reads regulations PDF
- Splits into chunks
- Embeds and stores into ChromaDB (batched ingestion)

### backend/app/vectordb/retriever.py
- Runs similarity search in ChromaDB for each clause
- Limits length of returned rules to keep LLM prompt small

### backend/app/llm/ollama_client.py
- Initializes Ollama LLM and embedding model
- Uses:
  - `nomic-embed-text` for embeddings
  - `llama3` for compliance reasoning

### backend/app/services/compliance_service.py
- Core compliance logic:
  - clause splitting
  - retrieval
  - single bulk LLM call
  - returns structured audit response

### backend/app/logger.py
- Creates logger instance
- Logs to:
  - console
  - `backend/logs/app.log` using rotating file handler

### backend/app/exceptions.py + middlewares.py
- Defines custom exceptions
- middleware handles exceptions gracefully:
  - avoids crashes
  - returns JSON error to UI

### streamlit_app/app.py
- UI for ingestion and compliance checking
- Displays structured compliance report with detailed remediation

---

## 8) Setup Instructions (Step-by-Step)

### 8.1 Prerequisites
- Python 3.12+
- Ollama installed
- Windows PowerShell
- Stable CPU/RAM (LLM inference can be heavy)

---

## 9) Running Ollama (Required)

### 9.1 Verify Ollama
```powershell
ollama list
```

### 9.2 Required models
Embedding model:
```powershell
ollama pull nomic-embed-text
```

LLM model:
```powershell
ollama pull llama3
```

---

## 10) Backend Setup

Go to backend folder:

```powershell
cd C:\Users\User\compliance-checker\backend
```

Create venv:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Install deps:

```powershell
pip install -r requirements.txt
pip install python-multipart
```

Run backend:

```powershell
python -m uvicorn app.main:app --reload
```

Swagger docs:
- http://127.0.0.1:8000/docs

---

## 11) Auto Regulations Ingest

Place regulations PDF here:

`backend/app/data/regulations_master.pdf`

On backend startup:
- if ChromaDB is empty (`count == 0`)
- regulations auto ingested

Check vector count:

- http://127.0.0.1:8000/db/count

Expected:
```json
{"count": 300}
```

---

## 12) Streamlit Setup

Open a new terminal:

```powershell
cd C:\Users\User\compliance-checker\backend
.\venv\Scripts\activate
cd ..\streamlit_app
streamlit run app.py
```

UI:
- http://localhost:8501

---

## 13) Testing (Pytest + Coverage)

Install:

```powershell
pip install pytest pytest-cov httpx
```

Run tests:

```powershell
pytest
```

Coverage terminal:

```powershell
pytest --cov=app --cov-report=term-missing
```

Coverage HTML:

```powershell
pytest --cov=app --cov-report=html
```

Open:
`backend/htmlcov/index.html`

---

## 14) Logging

Logs stored at:

`backend/logs/app.log`

Useful for:
- ingest progress
- failures
- LLM response issues
- PDF parsing errors

---

## 15) Things To Take Care Of (Important Notes)

### 15.1 If compliance check is slow
- Ensure you are using `nomic-embed-text` embeddings (fast)
- Keep `top_k=2`
- Keep clauses capped to 10
- Use smaller LLM if machine is slow (`phi3`, `mistral`)

### 15.2 PDF parsing quality
Some PDFs are scanned images.
This system reads only selectable text PDFs.
If the PDF is image-based, OCR is needed (future upgrade).

### 15.3 Regulations file size
Large regulations produce too many chunks.
Use `max_chunks` slider in Streamlit to control ingestion.

### 15.4 ChromaDB vector store persistence
Vectors persist in:
`backend/chroma_store/chroma.sqlite3`

Deleting `chroma_store/` resets the DB.

### 15.5 Always use venv
If you see `ModuleNotFoundError`, most likely venv not activated.

---

## 16) Limitations

- Not a replacement for professional legal advice
- LLM may produce incorrect reasoning if the rules are incomplete
- Best results require clean clause formatting

---

## 17) Future Enhancements

- Support OCR for scanned PDFs
- Multi-regulation knowledge bases + versioning
- Export audit report as PDF
- User accounts + role management
- Background ingestion jobs with progress tracking
- Redis caching for faster repeated checks

---

## 18) License
Educational prototype / internal R&D usage.
