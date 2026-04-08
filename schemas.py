from pydantic import BaseModel, Field
from typing import Optional, Any


class TranslationRequest(BaseModel):
    raw_text: str = Field(..., description="Raw unstructured text to translate", min_length=1)
    output_schema: Optional[str] = Field(None, description="Optional target JSON schema hint")
    chunk_for_rag: bool = Field(True, description="Whether to generate RAG-ready chunks")
    chunk_size: int = Field(500, description="Word count per RAG chunk", ge=100, le=2000)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "raw_text": "Invoice #4521. Date: Jan 5 2025. Client: Acme Corp. Total: $3550.",
                    "chunk_for_rag": True,
                    "chunk_size": 300,
                }
            ]
        }
    }


class RAGChunk(BaseModel):
    chunk_id: str
    text: str
    char_count: int
    word_count: int
    chunk_index: int
    metadata: dict


class TranslationMetadata(BaseModel):
    raw_char_count: int
    raw_word_count: int
    structured_fields: list[str]
    record_count: int
    compression_ratio: float
    rag_ready: bool


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


class TranslationResponse(BaseModel):
    structured_data: Any
    rag_chunks: list[RAGChunk]
    metadata: TranslationMetadata
    token_usage: TokenUsage


class BatchResult(BaseModel):
    index: int
    status: str
    data: Optional[TranslationResponse] = None
    error: Optional[str] = None


class BatchResponse(BaseModel):
    batch_size: int
    successful: int
    failed: int
    results: list[BatchResult]


class HealthResponse(BaseModel):
    status: str
    version: str
    claude_model: str
