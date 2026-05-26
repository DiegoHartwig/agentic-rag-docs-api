from unittest.mock import MagicMock, patch

import numpy as np
import pytest


def _make_service(provider="fastembed", model="BAAI/bge-small-en-v1.5"):
    """Instancia EmbeddingService com TextEmbedding mockado."""
    mock_model = MagicMock()
    with (
        patch("app.ingestion.embeddings.get_settings") as mock_settings,
        patch("fastembed.TextEmbedding", return_value=mock_model),
    ):
        settings = MagicMock()
        settings.EMBEDDING_PROVIDER = provider
        settings.EMBEDDING_MODEL = model
        mock_settings.return_value = settings

        from app.ingestion.embeddings import EmbeddingService

        service = EmbeddingService()
        service._model = mock_model
        return service, mock_model


def test_embed_text_calls_model():
    service, mock_model = _make_service()
    mock_model.embed.return_value = iter([np.array([0.1, 0.2, 0.3])])

    result = service.embed_text("texto de teste")

    mock_model.embed.assert_called_once_with(["texto de teste"])
    assert result == pytest.approx([0.1, 0.2, 0.3])


def test_embed_texts_calls_model():
    service, mock_model = _make_service()
    mock_model.embed.return_value = iter([
        np.array([0.1, 0.2]),
        np.array([0.3, 0.4]),
    ])

    result = service.embed_texts(["texto um", "texto dois"])

    mock_model.embed.assert_called_once_with(["texto um", "texto dois"])
    assert len(result) == 2
    assert result[0] == pytest.approx([0.1, 0.2])
    assert result[1] == pytest.approx([0.3, 0.4])


def test_embed_text_empty_raises():
    service, _ = _make_service()
    with pytest.raises(ValueError, match="vazio"):
        service.embed_text("")


def test_embed_text_whitespace_raises():
    service, _ = _make_service()
    with pytest.raises(ValueError, match="vazio"):
        service.embed_text("   ")


def test_embed_texts_empty_list_raises():
    service, _ = _make_service()
    with pytest.raises(ValueError, match="vazia"):
        service.embed_texts([])


def test_invalid_provider_raises():
    with patch("app.ingestion.embeddings.get_settings") as mock_settings:
        settings = MagicMock()
        settings.EMBEDDING_PROVIDER = "openai"
        settings.EMBEDDING_MODEL = "text-embedding-3-small"
        mock_settings.return_value = settings

        from app.ingestion.embeddings import EmbeddingService

        with pytest.raises(ValueError, match="não suportado"):
            EmbeddingService()
