from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import translate
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="AI Data Translation Layer",
    description="""
## 🧠 AI Data Translation Layer

Convert **messy, unstructured documents** into clean, structured, AI-ready datasets
for LLM & RAG pipelines — powered by **Anthropic Claude**.

### Key Features
- 📄 Text, TXT & CSV ingestion
- 🤖 Claude-powered intelligent field extraction & normalization
- 🗂️ Custom output schema support
- 🔍 RAG-ready chunking with metadata tagging
- 📦 Batch processing (up to 10 documents)
- 📊 Token usage tracking per request
""",
    version="1.0.0",
    contact={
        "name": "Sopan",
        "url": "https://github.com/yourusername/ai-data-translation-layer",
    },
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate.router, prefix="/api/v1", tags=["Translation"])


@app.get("/", tags=["Root"])
def root():
    return {
        "service": "AI Data Translation Layer",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "translate_text": "/api/v1/translate",
            "translate_file": "/api/v1/translate/file",
            "translate_batch": "/api/v1/translate/batch",
            "health": "/api/v1/health",
        },
    }
