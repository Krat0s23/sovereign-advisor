import os
import uuid
from datetime import datetime

import requests
import streamlit as st
from fpdf import FPDF

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Sovereign Advisor", page_icon="🛡️", layout="wide")


def safe_filename(value: str) -> str:
    value = (value or "chat_log").strip().replace(" ", "_").lower()
    cleaned = "".join(ch for ch in value if ch.isalnum() or ch in {"_", "-"})
    return cleaned or "chat_log"


def sanitize_pdf_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text).replace("\r\n", "\n").replace("\r", "\n")
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


def make_transcript(messages, title):
    lines = [
        f"Chat Title: {title}",
        f"Exported At: {datetime.utcnow().isoformat()} UTC",
        "",
    ]
    for msg in messages:
        role = msg.get("role", "assistant").upper()
        content = msg.get("content", "")
        lines.append(f"{role}:")
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def make_pdf_bytes(messages, title):
    pdf = FPDF(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    left_margin = 15
    right_margin = 15
    usable_width = 210 - left_margin - right_margin

    pdf.set_left_margin(left_margin)
    pdf.set_right_margin(right_margin)
    pdf.set_x(left_margin)

    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(usable_width, 8, sanitize_pdf_text(f"Chat Title: {title}"))

    pdf.ln(1)
    pdf.set_x(left_margin)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        usable_width,
        7,
        sanitize_pdf_text(f"Exported At: {datetime.utcnow().isoformat()} UTC"),
    )

    pdf.ln(3)

    if not messages:
        pdf.set_x(left_margin)
        pdf.multi_cell(usable_width, 7, "No messages in this conversation yet.")
    else:
        for msg in messages:
            role = sanitize_pdf_text(msg.get("role", "assistant").upper())
            content = sanitize_pdf_text(msg.get("content", "")) or "(empty)"

            pdf.set_x(left_margin)
            pdf.set_font("Helvetica", "B", 12)
            pdf.multi_cell(usable_width, 7, f"{role}:")

            pdf.set_x(left_margin)
            pdf.set_font("Helvetica", "", 11)
            for paragraph in content.split("\n") or [""]:
                paragraph = paragraph.strip()
                pdf.set_x(left_margin)
                pdf.multi_cell(usable_width, 7, paragraph if paragraph else " ")
            pdf.ln(2)

    return bytes(pdf.output(dest="S"))


if "sessions" not in st.session_state:
    session_id = str(uuid.uuid4())
    st.session_state.sessions = {
        session_id: {
            "title": "New chat",
            "messages": [],
            "mode": "auto",
        }
    }
    st.session_state.current_session_id = session_id

with st.sidebar:
    st.title("Sovereign Advisor")
    st.caption("Chat normally or ask for sovereign architecture guidance")

    st.markdown("### Chats")
    for session_id, session in st.session_state.sessions.items():
        label = session["title"][:40] if session["title"] else "Untitled chat"
        if st.button(label, key=f"chat_{session_id}", use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

    if st.button("Start new conversation", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.sessions[new_id] = {
            "title": "New chat",
            "messages": [],
            "mode": "auto",
        }
        st.session_state.current_session_id = new_id
        st.rerun()

    current_session = st.session_state.sessions[st.session_state.current_session_id]
    current_session["mode"] = "auto"

    st.markdown("### Export chat")
    transcript = make_transcript(current_session["messages"], current_session["title"])

    st.download_button(
        label="Download chat as TXT",
        data=transcript,
        file_name=f"{safe_filename(current_session['title'])}_chat_log.txt",
        mime="text/plain",
        use_container_width=True,
    )

    try:
        pdf_bytes = make_pdf_bytes(current_session["messages"], current_session["title"])
        st.download_button(
            label="Download chat as PDF",
            data=pdf_bytes,
            file_name=f"{safe_filename(current_session['title'])}_chat_log.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as exc:
        st.caption(f"PDF export temporarily unavailable: {exc}")

    st.markdown("### What this bot can do")
    st.markdown(
        "- Chat normally about general topics\n"
        "- Compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated\n"
        "- Evaluate sovereignty and residency constraints\n"
        "- Explain compliance-driven tradeoffs\n"
        "- Stream responses in real time"
    )

st.title("🛡️ Sovereign Advisor")
st.write(
    "Chat normally, or ask about IBM HashiCorp Vault Enterprise, HCP Vault Dedicated, sovereignty, compliance, residency, or deployment tradeoffs."
)

current_session = st.session_state.sessions[st.session_state.current_session_id]
current_session["mode"] = "auto"

for msg in current_session["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def stream_backend_response(payload: dict):
    with requests.post(
        f"{API_BASE_URL}/chat/stream",
        json=payload,
        timeout=180,
        stream=True,
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


prompt = st.chat_input("Ask anything, or compare Vault Enterprise vs HCP Vault Dedicated...")
if prompt:
    if current_session["title"] == "New chat":
        current_session["title"] = prompt[:50]

    current_session["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "message": prompt,
        "session_id": st.session_state.current_session_id,
        "user_id": "default-user",
        "mode": current_session["mode"],
    }

    try:
        with st.chat_message("assistant"):
            full_response = st.write_stream(stream_backend_response(payload))

        current_session["messages"].append(
            {
                "role": "assistant",
                "content": full_response,
            }
        )

    except Exception as exc:
        error_msg = f"Backend error: {exc}"
        current_session["messages"].append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)
