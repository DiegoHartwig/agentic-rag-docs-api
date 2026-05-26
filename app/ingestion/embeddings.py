from app.core.config import get_settings

_SUPPORTED_PROVIDERS = {"fastembed"}


class EmbeddingError(Exception):
    pass


class EmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self._provider = settings.EMBEDDING_PROVIDER
        self._model_name = settings.EMBEDDING_MODEL

        if self._provider not in _SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Provider de embeddings '{self._provider}' não suportado. "
                f"Providers disponíveis: {', '.join(sorted(_SUPPORTED_PROVIDERS))}."
            )

        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=self._model_name)

    def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("O texto para embedding não pode estar vazio.")
        try:
            return next(iter(self._model.embed([text]))).tolist()
        except Exception as e:
            raise EmbeddingError("Falha ao gerar embedding do texto.") from e

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            raise ValueError("A lista de textos para embedding não pode estar vazia.")
        try:
            return [vec.tolist() for vec in self._model.embed(texts)]
        except Exception as e:
            raise EmbeddingError("Falha ao gerar embeddings dos textos.") from e
