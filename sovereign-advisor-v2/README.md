# Sovereign Advisor v2

Air-gapped conversational chatbot for sovereign infrastructure recommendations.

## Stack
- Streamlit UI
- FastAPI backend
- Ollama local model serving
- IBM Granite via Ollama model name configuration
- Local chat history persistence
- Qdrant-ready vector store integration
- LangGraph-style orchestration scaffolding

## Run
```bash
docker compose up --build
```

## Notes
- Default model name is configurable with `OLLAMA_MODEL`.
- Default storage paths are local directories under `./data`.
- This scaffold preserves air-gapped deployment assumptions.
