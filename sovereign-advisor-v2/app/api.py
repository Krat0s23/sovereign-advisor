from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import re
import requests

from app.rag.router import route_query
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


def normalize_text(message: str) -> str:
    return re.sub(r"\s+", " ", message.strip().lower())


def match_small_talk(message: str) -> str | None:
    text = normalize_text(message)

    patterns = [
        (
            r"^(hi|hello|hey|yo|hii|hello there|good morning|good afternoon|good evening)[!. ]*$",
            "Hello! How can I help with Vault Enterprise, HCP Vault Dedicated, sovereignty, or compliance?",
        ),
        (
            r"^(how are you|how are you doing|how's it going|how is it going|how are things)\??$",
            "I'm doing well, thanks. I can help compare Vault Enterprise and HCP Vault Dedicated, explain sovereignty tradeoffs, or discuss compliance requirements.",
        ),
        (
            r"^(thanks|thank you|thanks a lot|thank you so much)[!. ]*$",
            "You're welcome. Ask me anything about Vault Enterprise, HCP Vault Dedicated, sovereignty, residency, or compliance.",
        ),
        (
            r"^(bye|goodbye|see you|talk to you later)[!. ]*$",
            "Goodbye! Reach out anytime you want help with Vault architecture, sovereignty, or compliance decisions.",
        ),
        (
            r"^(what can you do|help|what do you do|who are you)\??$",
            "I can compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated, evaluate sovereignty and residency constraints, and explain compliance-driven tradeoffs.",
        ),
    ]

    for pattern, response in patterns:
        if re.fullmatch(pattern, text):
            return response

    return None


def is_common_comparison_query(message: str) -> bool:
    text = normalize_text(message)

    comparison_signals = [
        "compare",
        "comparison",
        "difference",
        "differences",
        "vs",
        "versus",
        "which one",
        "should i choose",
        "recommend",
        "vault enterprise",
        "hcp vault dedicated",
        "sovereignty",
        "residency",
        "compliance",
        "fips",
        "hsm",
        "air-gap",
        "air gap",
        "seal wrap",
        "customer-controlled hsm",
        "deployment",
        "tradeoff",
        "tradeoffs",
        "deployment tradeoffs",
        "deployment model",
        "managed",
        "self-managed",
        "self managed",
    ]

    matches = sum(1 for term in comparison_signals if term in text)
    return matches >= 1


def build_fast_comparison_answer(message: str) -> tuple[str, list[str]]:
    text = normalize_text(message)

    route = [
        "vault_enterprise_docs",
        "hcp_vault_dedicated_docs",
        "sovereignty_guidelines",
    ]

    if any(term in text for term in ["fips", "hsm", "air-gap", "air gap", "seal wrap", "customer-controlled hsm"]):
        answer = (
            "Recommendation: IBM HashiCorp Vault Enterprise.\n\n"
            "- Choose Vault Enterprise when you need customer-controlled HSM boundaries, strict FIPS-oriented controls, or hard isolation requirements.\n"
            "- It is the stronger fit when security control boundaries matter more than operational convenience.\n"
            "- HCP Vault Dedicated is better when you prefer a managed service and do not require that same level of infrastructure control.\n"
            "- In short: for FIPS and HSM-backed control requirements, favor Vault Enterprise."
        )
    elif any(term in text for term in ["sovereignty", "residency", "data sovereignty"]):
        answer = (
            "Recommendation: IBM HashiCorp Vault Enterprise.\n\n"
            "- Vault Enterprise is usually the better choice when sovereignty, residency, and control boundaries are central requirements.\n"
            "- It gives you more control over where and how the platform is deployed and governed.\n"
            "- HCP Vault Dedicated is a strong managed option, but it does not offer the same level of customer-operated boundary control.\n"
            "- In short: if sovereignty and residency constraints are strict, favor Vault Enterprise."
        )
    else:
        answer = (
            "Here is the quick deployment tradeoff view:\n\n"
            "- IBM HashiCorp Vault Enterprise gives you more deployment control, stronger sovereignty alignment, and more flexibility for strict compliance or security boundaries.\n"
            "- HCP Vault Dedicated gives you a managed Vault experience with lower operational overhead and faster adoption.\n"
            "- Choose Vault Enterprise when customization, infrastructure control, residency, or advanced boundary requirements matter most.\n"
            "- Choose HCP Vault Dedicated when you want a simpler managed operating model.\n"
            "- In short: Vault Enterprise optimizes for control; HCP Vault Dedicated optimizes for convenience."
        )

    return answer, route


@app.get("/")
def home():
    return {"message": "Sovereign Advisor API Running"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    small_talk_response = match_small_talk(payload.message)
    if small_talk_response:
        return ChatResponse(
            answer=small_talk_response,
            recommendation=None,
            retrieved_docs=[],
            route=[],
        )

    if payload.mode in ["auto", "advisor"] and is_common_comparison_query(payload.message):
        fast_answer, route = build_fast_comparison_answer(payload.message)
        return ChatResponse(
            answer=fast_answer,
            recommendation={
                "recommended_products": route,
                "mode": payload.mode,
            },
            retrieved_docs=[],
            route=route,
        )

    route = route_query(payload.message)
    retrieval = retrieve_context(payload.message, route)

    context_block = "\n\n".join(
        [f"- {item['source']}: {item['text']}" for item in retrieval["chunks"][:3]]
    )

    prompt = (
        "You are Sovereign Advisor for IBM HashiCorp Vault.\n"
        "Compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated.\n"
        "Be concise and practical.\n"
        "If requirements mention hard air-gap, strong sovereignty, FIPS 140-2/140-3, seal wrap, "
        "or customer-controlled HSM boundaries, prefer IBM HashiCorp Vault Enterprise.\n"
        "Answer in 5 short bullet points maximum.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {payload.message}\n\n"
        "Answer:"
    )

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 220,
                    "num_ctx": 2048,
                    "top_k": 20,
                    "top_p": 0.9,
                },
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        answer = data.get("response", "No response returned from model.")

        recommendation = {
            "recommended_products": route,
            "mode": payload.mode,
        }

        return ChatResponse(
            answer=answer,
            recommendation=recommendation,
            retrieved_docs=retrieval["sources"],
            route=route,
        )

    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=500, detail=f"Ollama HTTP error: {detail}")
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {exc}")
