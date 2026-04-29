from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
import re
import requests

from app.rag.router import classify_intent, route_query
from app.rag.retriever import retrieve_context

app = FastAPI()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "granite3.1-dense:8b")


class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: str
    mode: str = "auto"


class ChatResponse(BaseModel):
    answer: str
    recommendation: dict | None = None
    retrieved_docs: list[str] = []
    route: list[str] = []
    intent: str = "chat"


def normalize_text(message: str) -> str:
    return re.sub(r"\s+", " ", message.strip().lower())


def match_local_utility(message: str) -> str | None:
    text = normalize_text(message)

    if "your name" in text or "who are you" in text:
        return "I'm Sovereign Advisor, your assistant for normal conversation and sovereign architecture guidance."

    if "time" in text:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    if ("day" in text and "today" in text) or text == "what day is it":
        return f"Today is {datetime.now().strftime('%A')}."

    if "date" in text:
        return f"Today's date is {datetime.now().strftime('%B %d, %Y')}."

    return None


def match_small_talk(message: str) -> str | None:
    text = normalize_text(message)

    patterns = [
        (
            r"^(hi|hello|hey|yo|hii|hello there|good morning|good afternoon|good evening)[!. ]*$",
            "Hello! I can chat normally, and I can also help compare Vault Enterprise and HCP Vault Dedicated, including sovereignty and residency tradeoffs.",
        ),
        (
            r"^(how are you|how are you doing|how's it going|how is it going|how are things)\??$",
            "I'm doing well, thanks. I can chat normally or help as a sovereign advisor for Vault Enterprise, HCP Vault Dedicated, compliance, residency, and deployment decisions.",
        ),
        (
            r"^(thanks|thank you|thanks a lot|thank you so much)[!. ]*$",
            "You're welcome.",
        ),
        (
            r"^(bye|goodbye|see you|talk to you later)[!. ]*$",
            "Goodbye!",
        ),
        (
            r"^(what can you do|help|what do you do)\??$",
            "I can have normal conversations, and I can also act as a sovereign advisor to compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated, evaluate sovereignty and residency constraints, and explain compliance-driven tradeoffs.",
        ),
    ]

    for pattern, response in patterns:
        if re.fullmatch(pattern, text):
            return response

    return None


def build_system_prompt(intent: str) -> str:
    if intent == "advisor":
        return (
            "You are Sovereign Advisor for IBM HashiCorp Vault. "
            "Help customers compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated. "
            "Be precise about sovereignty, residency, compliance, control boundaries, HSM, FIPS, and deployment tradeoffs. "
            "If requirements mention hard air-gap, strong sovereignty, FIPS 140-2/140-3, seal wrap, "
            "or customer-controlled HSM boundaries, explain why Vault Enterprise is usually the better fit. "
            "Be concise, practical, and direct."
        )

    return (
        "You are a helpful, concise, natural conversational assistant. "
        "Answer clearly and normally. "
        "If the user asks about IBM HashiCorp Vault Enterprise, HCP Vault Dedicated, sovereignty, residency, "
        "compliance, or deployment tradeoffs, provide helpful domain-aware answers."
    )


def build_prompt(message: str, intent: str) -> tuple[str, list[str], dict]:
    route = route_query(message) if intent == "advisor" else []
    retrieval = retrieve_context(message, route) if route else {"chunks": [], "sources": []}

    context_block = "\n\n".join(
        [f"- {item['source']}: {item['text']}" for item in retrieval["chunks"][:3]]
    )

    system_prompt = build_system_prompt(intent)

    if intent == "advisor" and context_block:
        prompt = (
            f"{system_prompt}\n\n"
            f"Context:\n{context_block}\n\n"
            f"Question: {message}\n\n"
            "Answer with practical guidance. Use bullets when helpful."
        )
    else:
        prompt = (
            f"{system_prompt}\n\n"
            f"User message: {message}\n\n"
            "Answer naturally and clearly."
        )

    return prompt, route, retrieval


def ollama_payload(prompt: str) -> dict:
    return {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "options": {
            "temperature": 0.3,
            "num_predict": 320,
            "num_ctx": 2048,
            "top_k": 30,
            "top_p": 0.9,
        },
    }


@app.get("/")
def home():
    return {"message": "Sovereign Advisor API Running"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    local_utility_response = match_local_utility(payload.message)
    if local_utility_response:
        return ChatResponse(
            answer=local_utility_response,
            recommendation=None,
            retrieved_docs=[],
            route=[],
            intent="chat",
        )

    small_talk_response = match_small_talk(payload.message)
    if small_talk_response:
        return ChatResponse(
            answer=small_talk_response,
            recommendation=None,
            retrieved_docs=[],
            route=[],
            intent="chat",
        )

    intent = classify_intent(payload.message)
    prompt, route, retrieval = build_prompt(payload.message, intent)

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                **ollama_payload(prompt),
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        recommendation = None
        if intent == "advisor":
            recommendation = {
                "recommended_products": route,
                "mode": payload.mode,
            }

        return ChatResponse(
            answer=data.get("response", "No response returned from model."),
            recommendation=recommendation,
            retrieved_docs=retrieval["sources"],
            route=route,
            intent=intent,
        )

    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 500
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=500, detail=f"Ollama HTTP {status}: {detail}")
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {exc}")


@app.post("/chat/stream")
def chat_stream(payload: ChatRequest):
    local_utility_response = match_local_utility(payload.message)
    if local_utility_response:
        def local_utility_generator():
            yield local_utility_response
        return StreamingResponse(local_utility_generator(), media_type="text/plain")

    small_talk_response = match_small_talk(payload.message)
    if small_talk_response:
        def small_talk_generator():
            yield small_talk_response
        return StreamingResponse(small_talk_generator(), media_type="text/plain")

    intent = classify_intent(payload.message)
    prompt, route, retrieval = build_prompt(payload.message, intent)

    def generate():
        try:
            with requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    **ollama_payload(prompt),
                    "stream": True,
                },
                timeout=180,
                stream=True,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    text = chunk.get("response", "")
                    if text:
                        yield text

        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            detail = exc.response.text if exc.response is not None else str(exc)
            yield f"\n\n[Error: Ollama HTTP {status}: {detail}]"
        except requests.RequestException as exc:
            yield f"\n\n[Error: Ollama request failed: {exc}]"
        except Exception as exc:
            yield f"\n\n[Error: Unexpected streaming failure: {exc}]"

    return StreamingResponse(generate(), media_type="text/plain")
