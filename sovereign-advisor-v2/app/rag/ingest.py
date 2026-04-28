from qdrant_client import models
from app.rag.store import get_qdrant_client, ensure_collection, COLLECTIONS, VECTOR_SIZE
from app.rag.embedder import embed_text

def upsert_docs(bucket: str, docs: list[dict]):
    client = get_qdrant_client()
    collection_name = COLLECTIONS[bucket]
    ensure_collection(collection_name)

    points = []
    for idx, doc in enumerate(docs):
        points.append(
            models.PointStruct(
                id=idx,
                vector=embed_text(doc["text"]),
                payload=doc,
            )
        )

    client.upsert(collection_name=collection_name, points=points)
