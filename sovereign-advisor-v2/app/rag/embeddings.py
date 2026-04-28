import os
from functools import lru_cache
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]
