import os
import uuid
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

st.set_page_config(page_title="Sovereign Advisor", page_icon="🛡️", layout="wide")

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

current_session = st.session_state.sessions[st.session_state.current_session_id]

with st.sidebar:
    st.title("Sovereign Advisor")
    st.caption("IBM HashiCorp Vault deployment advisor")

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
    current_session["mode"] = st.selectbox(
        "Conversation mode",
        ["auto", "chat", "advisor"],
        index=["auto", "chat", "advisor"].index(current_session["mode"]),
    )

    st.markdown("### What this bot can do")
    st.markdown(
        "- Compare IBM HashiCorp Vault Enterprise and HCP Vault Dedicated\n"
        "- Evaluate sovereignty and residency constraints\n"
        "- Explain compliance-driven tradeoffs\n"
        "- Use routed document retrieval"
    )

st.title("🛡️ Sovereign Advisor")
st.write(
    "Ask about IBM HashiCorp Vault Enterprise, HCP Vault Dedicated, sovereignty, compliance, or target architecture."
)

current_session = st.session_state.sessions[st.session_state.current_session_id]

for msg in current_session["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about Vault Enterprise vs HCP Vault Dedicated...")
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
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=180)
        response.raise_for_status()
        result = response.json()

        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
        }
        current_session["messages"].append(assistant_message)

        with st.chat_message("assistant"):
            st.markdown(result["answer"])
    except Exception as exc:
        error_msg = f"Backend error: {exc}"
        current_session["messages"].append({"role": "assistant", "content": error_msg})
        with st.chat_message("assistant"):
            st.error(error_msg)
