import os
import requests
from typing import List, Dict

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite3.1-dense:8b")


def chat(messages: List[Dict[str, str]]) -> str:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("message", {}).get("content", "")
