from fastembed import TextEmbedding

class EmbeddingService:
    
    def __init__(self):
        self.embedding = TextEmbedding()
    
    def get_embedding(self, text: str) -> list:
        return list(next(self.embedding.embed([text])))