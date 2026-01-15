"""Test to verify Gemini API key is valid and working."""

import os
import requests
import pytest
from dotenv import load_dotenv


load_dotenv()


@pytest.fixture
def api_key():
    """Load Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set in environment")
    return key


def test_gemini_api_key_works(api_key):
    """Verify API key by requesting a programming joke from Gemini 2.5 Flash."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Tell me a short programming joke."}
                ]
            }
        ]
    }

    response = requests.post(url, json=payload, timeout=30)

    assert response.status_code == 200, f"API request failed: {response.status_code} - {response.text}"

    data = response.json()
    assert "candidates" in data, "Response missing 'candidates' field"
    assert len(data["candidates"]) > 0, "No candidates in response"

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    assert len(text) > 0, "Empty response from Gemini"

    print(f"\nGemini responded with: {text}")
