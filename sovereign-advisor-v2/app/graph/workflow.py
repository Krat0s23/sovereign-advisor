import re
from app.llm.ollama_client import chat as ollama_chat
from app.memory.history import append_message, get_thread_messages
from app.rag.ingest import ingest_documents
from app.rag.retrieve import retrieve
from app.recommend import recommend


def detect_mode(message: str, requested_mode: str) -> str:
    if requested_mode in {"chat", "advisor"}:
        return requested_mode
    pattern = r"\b(compliance|residency|sovereignty|recommend|hcp|self-managed|self managed|ownership|deployment|architecture|vault|terraform)\b"
    return "advisor" if re.search(pattern, message.lower()) else "chat"


def extract_profile(message: str) -> dict:
    text = message.lower()
    return {
        "geo": "Europe" if "europe" in text or "eu" in text else "India" if "india" in text else "Unknown",
        "compliance": "High" if "high compliance" in text or "regulated" in text else "Medium",
        "ownership": "Managed Service" if "managed" in text else "Customer Managed" if "self-managed" in text or "customer managed" in text else "Managed Service",
        "growth": "Enterprise Scale" if "scale" in text or "growth" in text else "Unknown",
        "data_residency": "Strict" if "strict" in text or "residency" in text or "sovereign" in text else "Flexible",
        "workload": "Vault" if "vault" in text else "Terraform" if "terraform" in text else "General",
    }


def build_system_prompt(mode: str, retrieved_docs: list[dict]) -> str:
    context = "\n\n".join(
        [f"Source: {doc['source']}\nContent: {doc['text']}" for doc in retrieved_docs]
    )
    if mode == "advisor":
        return (
            "You are Sovereign Advisor, an air-gapped infrastructure recommendation assistant. "
            "Answer clearly and keep advice grounded in the retrieved local knowledge. "
            "If information is missing, ask clarifying questions.\n\n"
            f"Retrieved context:\n{context}"
        )
    return (
        "You are Sovereign Advisor, a helpful enterprise infrastructure chatbot running in an air-gapped environment. "
        "Use the retrieved local knowledge when helpful and do not invent unsupported compliance claims.\n\n"
        f"Retrieved context:\n{context}"
    )


def run_chat_turn(thread_id: str, user_id: str, message: str, mode: str = "auto") -> dict:
    ingest_documents()
    resolved_mode = detect_mode(message, mode)
    retrieved_docs = retrieve(message, limit=3)
    history = get_thread_messages(thread_id)[-8:]

    messages = [{"role": "system", "content": build_system_prompt(resolved_mode, retrieved_docs)}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": message})

    append_message(thread_id, "user", message, {"user_id": user_id, "mode": resolved_mode})

    recommendation = None
    if resolved_mode == "advisor":
        profile = extract_profile(message)
        recommendation = recommend(profile)
        messages.append({
            "role": "system",
            "content": "Recommendation context: " + recommendation["reason"],
        })

    answer = ollama_chat(messages)
    if not answer:
        answer = "I could not generate a response from the local model. Verify that Ollama is running and the Granite model is available locally."

    append_message(thread_id, "assistant", answer, {
        "mode": resolved_mode,
        "retrieved_docs": [doc["source"] for doc in retrieved_docs],
        "recommendation": recommendation,
    })

    return {
        "answer": answer,
        "thread_id": thread_id,
        "mode": resolved_mode,
        "recommendation": recommendation,
        "retrieved_docs": [doc["source"] for doc in retrieved_docs],
    }
