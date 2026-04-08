import io
import csv
import json
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.models.schemas import (
    TranslationRequest, TranslationResponse,
    BatchResponse, BatchResult, HealthResponse
)
from app.services import translator
from app.utils.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="healthy", version="1.0.0", claude_model=settings.claude_model)


@router.post("/translate", response_model=TranslationResponse, summary="Translate raw text")
async def translate_text(request: TranslationRequest):
    """
    Translate raw unstructured text into clean structured JSON,
    with optional RAG chunking.
    """
    try:
        return await translator.translate(
            raw_text=request.raw_text,
            output_schema=request.output_schema,
            do_chunk=request.chunk_for_rag,
            chunk_size=request.chunk_size,
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate/file", response_model=TranslationResponse, summary="Translate uploaded file")
async def translate_file(
    file: UploadFile = File(...),
    output_schema: Optional[str] = Query(None),
    chunk_for_rag: bool = Query(True),
    chunk_size: int = Query(500),
):
    """
    Upload a `.txt` or `.csv` file and translate it to structured JSON.
    """
    if not (file.filename.endswith(".txt") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only .txt and .csv files are supported")

    content = await file.read()
    try:
        raw_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = content.decode("latin-1")

    if file.filename.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(raw_text))
        raw_text = json.dumps(list(reader), indent=2)

    try:
        return await translator.translate(
            raw_text=raw_text,
            output_schema=output_schema,
            do_chunk=chunk_for_rag,
            chunk_size=chunk_size,
        )
    except Exception as e:
        logger.error(f"File translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate/batch", response_model=BatchResponse, summary="Batch translate documents")
async def translate_batch(documents: list[str]):
    """
    Translate up to 10 raw documents in a single request.
    """
    if not documents:
        raise HTTPException(status_code=400, detail="documents list cannot be empty")
    if len(documents) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 documents per batch")

    results = []
    success_count = 0

    for i, doc in enumerate(documents):
        try:
            result = await translator.translate(raw_text=doc)
            results.append(BatchResult(index=i, status="success", data=result))
            success_count += 1
        except Exception as e:
            results.append(BatchResult(index=i, status="error", error=str(e)))

    return BatchResponse(
        batch_size=len(documents),
        successful=success_count,
        failed=len(documents) - success_count,
        results=results,
    )
