from fastembed import TextEmbedding

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding()
    return _model


class EmbeddingService:

    def __init__(self):
        self.embedding = _get_model()

    def get_embedding(self, text: str) -> list:
        return list(next(self.embedding.embed([text])))