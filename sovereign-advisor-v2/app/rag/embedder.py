from fastembed import TextEmbedding

_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _model

def embed_text(text: str):
    return list(get_embedder().embed([text]))[0].tolist()
