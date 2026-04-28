import os
from functools import lru_cache

from qdrant_client import QdrantClient, models

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
VECTOR_SIZE = 384

COLLECTIONS = {
    "vault_docs": "vault_docs",
    "boundary_docs": "boundary_docs",
    "terraform_docs": "terraform_docs",
    "vault_enterprise_docs": "vault_enterprise_docs",
    "hcp_vault_docs": "hcp_vault_docs",
    "hcp_vault_dedicated_docs": "hcp_vault_dedicated_docs",
    "sovereignty_guidelines": "sovereignty_guidelines",
}

@lru_cache(maxsize=1)
def get_qdrant_client():
    return QdrantClient(url=QDRANT_URL)

def ensure_collection(collection_name: str):
    client = get_qdrant_client()
    existing = {c.name for c in client.get_collections().collections}

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

    return client
