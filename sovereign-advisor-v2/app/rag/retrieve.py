from app.rag.embeddings import embed_texts
from app.rag.store import get_qdrant_client, ensure_collection, QDRANT_COLLECTION


def retrieve(query: str, limit: int = 3) -> list[dict]:
    ensure_collection()
    client = get_qdrant_client()
    vector = embed_texts([query])[0]
    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=vector,
        limit=limit,
    )
    documents = []
    for item in results:
        payload = item.payload or {}
        documents.append(
            {
                "source": payload.get("source", "unknown"),
                "text": payload.get("text", ""),
                "score": item.score,
            }
        )
    return documents
