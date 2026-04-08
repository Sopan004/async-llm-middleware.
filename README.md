# 🧠 AI Data Translation Layer

> **Convert messy, unstructured documents into clean, structured, AI-ready datasets for LLM & RAG pipelines — powered by Anthropic Claude.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Claude](https://img.shields.io/badge/Anthropic-Claude%20Sonnet-orange)](https://anthropic.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Problem Statement

Enterprises store vast amounts of data in unstructured formats — invoices, contracts, patient records, emails, reports — that are unusable by LLMs and RAG pipelines without preprocessing. Manual extraction is slow, inconsistent, and doesn't scale.

**AI Data Translation Layer solves this** by using Claude's intelligence to automatically extract, normalize, and structure any document into consistent JSON — ready for vector embedding and retrieval.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Claude-Powered Extraction** | Intelligent field detection, type inference & normalization |
| 📄 **Multi-Format Ingestion** | Raw text, `.txt`, `.csv` file upload |
| 🗂️ **Custom Schema Support** | Define your target JSON structure as a hint |
| 🔍 **RAG Chunking** | Auto-splits output into overlapping chunks with metadata |
| 📦 **Batch Processing** | Translate up to 10 documents per request |
| 💰 **Cost Tracking** | Token usage & estimated USD cost per request |
| 📖 **Auto Docs** | Swagger UI at `/docs`, ReDoc at `/redoc` |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│                Enterprise Application               │
└─────────────────────┬──────────────────────────────┘
                      │  HTTP Request (raw document)
                      ▼
┌────────────────────────────────────────────────────┐
│              AI Data Translation Layer             │
│                  (FastAPI Service)                 │
│                                                    │
│   /translate        → Raw text → structured JSON  │
│   /translate/file   → Upload .txt / .csv          │
│   /translate/batch  → Up to 10 docs at once       │
└─────────────────────┬──────────────────────────────┘
                      │  API Call
                      ▼
┌────────────────────────────────────────────────────┐
│           Anthropic Claude Sonnet API              │
│     (Extraction · Normalization · Structuring)     │
└─────────────────────┬──────────────────────────────┘
                      │
          ┌───────────┴──────────┐
          ▼                      ▼
  Structured JSON           RAG Chunks
  (clean output)       (with metadata tags)
          │                      │
          ▼                      ▼
   Your Database         Vector Store
  (PostgreSQL etc.)  (Pinecone / ChromaDB)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Anthropic API key](https://console.anthropic.com)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ai-data-translation-layer.git
cd ai-data-translation-layer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the server
uvicorn app.main:app --reload --port 8000
```

**API Docs:** http://localhost:8000/docs

---

## 📡 API Reference

### `POST /api/v1/translate`
Translate raw unstructured text to structured JSON.

**Request:**
```json
{
  "raw_text": "Invoice #4521. Date: Jan 5 2025. Client: Acme Corp. Total: $3550.",
  "output_schema": null,
  "chunk_for_rag": true,
  "chunk_size": 500
}
```

**Response:**
```json
{
  "structured_data": {
    "invoice_number": "4521",
    "date": "2025-01-05",
    "client": { "name": "Acme Corp" },
    "total_due": 3550
  },
  "rag_chunks": [
    {
      "chunk_id": "chunk_0000",
      "text": "{ \"invoice_number\": \"4521\" ...",
      "word_count": 42,
      "metadata": { "ready_for_embedding": true }
    }
  ],
  "metadata": {
    "raw_char_count": 68,
    "structured_fields": ["invoice_number", "date", "client", "total_due"],
    "record_count": 1,
    "rag_ready": true
  },
  "token_usage": {
    "input_tokens": 180,
    "output_tokens": 95,
    "estimated_cost_usd": 0.00197
  }
}
```

### `POST /api/v1/translate/file`
Upload a `.txt` or `.csv` file.

### `POST /api/v1/translate/batch`
Send an array of up to 10 raw document strings.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
ai-data-translation-layer/
├── app/
│   ├── main.py                 # FastAPI app + CORS
│   ├── routers/
│   │   └── translate.py        # API route handlers
│   ├── services/
│   │   └── translator.py       # Core Claude extraction logic
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── utils/
│       ├── config.py           # Environment settings
│       └── logger.py           # Structured logging
├── tests/
│   └── test_translate.py       # Unit tests
├── examples/
│   ├── sample_invoice.txt      # Demo input document
│   └── api_requests.sh         # Example curl commands
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🗺️ Roadmap

- [ ] PDF ingestion (PyMuPDF)
- [ ] DOCX / Excel support
- [ ] Direct vector DB push (Pinecone, ChromaDB, Weaviate)
- [ ] Schema template library (invoices, medical, legal, HR, finance)
- [ ] API key authentication middleware
- [ ] Async batch processing with job queue (Celery + Redis)
- [ ] React dashboard UI
- [ ] Docker + Docker Compose setup
- [ ] Deploy to Render / Railway (one-click)

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **AI:** Anthropic Claude Sonnet (claude-sonnet-4-20250514)
- **Validation:** Pydantic v2
- **Testing:** Pytest, HTTPX
- **Deployment:** Render / Railway / AWS Lambda

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](LICENSE)

---

## 👤 Author

**Sopan** — AI/ML Engineer & Entrepreneur  
🔗 [LinkedIn](https://linkedin.com/in/yourprofile) · [Portfolio](https://yourportfolio.com) · [GitHub](https://github.com/yourusername)
