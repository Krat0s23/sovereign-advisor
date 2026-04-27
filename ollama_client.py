import requests

def ask_ollama(prompt):
    response = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]
