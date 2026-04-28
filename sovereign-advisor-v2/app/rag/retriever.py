from app.rag.store import get_qdrant_client, ensure_collection, COLLECTIONS
from app.rag.embedder import embed_text

MAX_CHARS_PER_CHUNK = 500

def retrieve_context(query: str, route: list[str], limit: int = 2):
    client = get_qdrant_client()
    chunks = []
    sources = []

    for bucket in route:
        collection_name = COLLECTIONS[bucket]
        ensure_collection(collection_name)
        query_vector = embed_text(query)

        response = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
        )

        results = response.points if hasattr(response, "points") else []

        for item in results:
            payload = item.payload or {}
            text = payload.get("text", "")
            if text:
                text = text[:MAX_CHARS_PER_CHUNK].strip()
                chunks.append({
                    "source": bucket,
                    "text": text,
                })

            source_file = payload.get("source_file")
            if source_file:
                sources.append(source_file)

    return {
        "chunks": chunks[:4],
        "sources": list(dict.fromkeys(sources)),
    }
