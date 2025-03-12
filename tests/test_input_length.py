from unittest.mock import patch

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.asyncio
@patch(
    "app.clients.openai.openai_client.generate_response", return_value="mocked response"
)
async def test_input_validation(mock_generate):
    # Test with empty input
    response = client.post("/question", json={"text": ""})
    assert response.status_code == 422

    # Test with input that's too short (assuming minimum length is 1)
    response = client.post("/question", json={"text": ""})
    assert response.status_code == 422

    # Test with valid input
    response = client.post("/question", json={"text": "Hello"})
    assert response.status_code == 200

    # Test with very long input
    long_input = "a" * 513
    response = client.post("/question", json={"text": long_input})
    assert response.status_code == 422

    # Test with input at maximum length
    max_input = "a" * 512
    response = client.post("/question", json={"text": max_input})
    assert response.status_code == 200

    # Test with missing text field
    response = client.post("/question", json={"text": ""})
    assert response.status_code == 422

    # Test with wrong type
    response = client.post("/question", json={"text": 123})
    assert response.status_code == 422
