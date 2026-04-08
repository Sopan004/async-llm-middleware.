import json
import re
from typing import Optional
import anthropic
from app.models.schemas import (
    TranslationResponse, RAGChunk, TranslationMetadata, TokenUsage
)
from app.utils.logger import get_logger
from app.utils.config import settings

logger = get_logger(__name__)

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Claude Sonnet pricing (per million tokens)
INPUT_COST_PER_M = 3.0
OUTPUT_COST_PER_M = 15.0


def build_extraction_prompt(raw_text: str, output_schema: Optional[str] = None) -> str:
    schema_hint = f"\nTarget schema hint: {output_schema}" if output_schema else ""
    return f"""You are an expert data extraction AI for enterprise systems.
Convert the following raw, messy document into clean, structured JSON.

Rules:
- Extract ALL meaningful fields and values
- Normalize inconsistent formatting (dates → ISO 8601, numbers → numeric type, names → Title Case)
- Use descriptive snake_case field names
- Group related fields into nested objects
- Set missing/unclear values to null
- If the document contains multiple records, return them as an array under "records"
- Detect and preserve data types (string, number, date, boolean, array)
{schema_hint}

Raw Document:
\"\"\"
{raw_text}
\"\"\"

Return ONLY valid JSON. No explanation, no markdown fences."""


def parse_claude_response(response_text: str) -> dict:
    """Safely parse Claude's JSON response, stripping any markdown."""
    text = response_text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed: {e}. Returning raw text.")
        return {"raw_extraction": text, "_parse_warning": "Auto-parse failed; raw text returned"}


def chunk_for_rag(structured_data: dict, chunk_size: int = 500) -> list[RAGChunk]:
    """Chunk structured JSON into overlapping RAG-ready segments."""
    chunks = []
    data_str = json.dumps(structured_data, indent=2)
    words = data_str.split()
    overlap = min(50, chunk_size // 5)

    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i: i + chunk_size]
        if not chunk_words:
            break
        chunk_text = " ".join(chunk_words)
        idx = i // step
        chunks.append(RAGChunk(
            chunk_id=f"chunk_{idx:04d}",
            text=chunk_text,
            char_count=len(chunk_text),
            word_count=len(chunk_words),
            chunk_index=idx,
            metadata={
                "source": "ai_data_translation_layer",
                "format": "structured_json",
                "ready_for_embedding": True,
            },
        ))

    return chunks


def build_metadata(raw_text: str, structured_data: dict) -> TranslationMetadata:
    fields = list(structured_data.keys()) if isinstance(structured_data, dict) else []
    records = structured_data.get("records", [structured_data])
    structured_str = json.dumps(structured_data)
    return TranslationMetadata(
        raw_char_count=len(raw_text),
        raw_word_count=len(raw_text.split()),
        structured_fields=fields,
        record_count=len(records) if isinstance(records, list) else 1,
        compression_ratio=round(len(structured_str) / max(len(raw_text), 1), 2),
        rag_ready=True,
    )


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return round(
        (input_tokens / 1_000_000 * INPUT_COST_PER_M)
        + (output_tokens / 1_000_000 * OUTPUT_COST_PER_M),
        6,
    )


async def translate(
    raw_text: str,
    output_schema: Optional[str] = None,
    do_chunk: bool = True,
    chunk_size: int = 500,
) -> TranslationResponse:
    logger.info(f"Translating document ({len(raw_text)} chars)")

    prompt = build_extraction_prompt(raw_text, output_schema)
    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    structured_data = parse_claude_response(message.content[0].text)
    rag_chunks = chunk_for_rag(structured_data, chunk_size) if do_chunk else []
    metadata = build_metadata(raw_text, structured_data)
    token_usage = TokenUsage(
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
        estimated_cost_usd=estimate_cost(
            message.usage.input_tokens, message.usage.output_tokens
        ),
    )

    logger.info(f"Translation complete. Tokens used: {message.usage.input_tokens + message.usage.output_tokens}")
    return TranslationResponse(
        structured_data=structured_data,
        rag_chunks=rag_chunks,
        metadata=metadata,
        token_usage=token_usage,
    )
