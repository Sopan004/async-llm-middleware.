import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "AI Data Translation Layer"


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("app.services.translator.client")
def test_translate_text(mock_client):
    mock_message = MagicMock()
    mock_message.content[0].text = '{"invoice_number": "4521", "total": 3550}'
    mock_message.usage.input_tokens = 100
    mock_message.usage.output_tokens = 50
    mock_client.messages.create.return_value = mock_message

    response = client.post("/api/v1/translate", json={
        "raw_text": "Invoice #4521. Total: $3550.",
        "chunk_for_rag": True,
        "chunk_size": 300
    })

    assert response.status_code == 200
    data = response.json()
    assert "structured_data" in data
    assert "rag_chunks" in data
    assert "metadata" in data
    assert data["metadata"]["rag_ready"] is True


def test_translate_empty_text():
    response = client.post("/api/v1/translate", json={"raw_text": ""})
    assert response.status_code == 422


def test_batch_too_many_docs():
    response = client.post("/api/v1/translate/batch", json=["doc"] * 11)
    assert response.status_code == 400
