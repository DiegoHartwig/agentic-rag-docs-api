from unittest.mock import MagicMock, patch

import pytest

from app.tools.retrieve_documents import retrieve_documents

_EMBEDDING_PATH = "app.tools.retrieve_documents.EmbeddingService"
_QDRANT_PATH = "app.tools.retrieve_documents.QdrantCollectionClient"

_FAKE_VECTOR = [0.1] * 384

_SAMPLE_RESULTS = [
    {
        "text": "Trino supports row-level security.",
        "score": 0.91,
        "document_id": "doc-1",
        "filename": "trino-security.pdf",
        "collection_name": "trino",
        "page": 3,
        "chunk_index": 12,
        "tags": ["trino", "security"],
        "source_type": "official_docs",
    },
    {
        "text": "Access control is configurable per connector.",
        "score": 0.78,
        "document_id": "doc-1",
        "filename": "trino-security.pdf",
        "collection_name": "trino",
        "page": 4,
        "chunk_index": 13,
        "tags": ["trino", "security"],
        "source_type": "official_docs",
    },
]


def _make_mocks(results=None, raise_value_error=False):
    mock_embed = MagicMock()
    mock_embed.embed_text.return_value = _FAKE_VECTOR

    mock_qdrant = MagicMock()
    if raise_value_error:
        mock_qdrant.search_similar_chunks.side_effect = ValueError("Collection não encontrada.")
    else:
        mock_qdrant.search_similar_chunks.return_value = (
            results if results is not None else _SAMPLE_RESULTS
        )

    return mock_embed, mock_qdrant


def test_retrieve_documents_returns_results():
    mock_embed, mock_qdrant = _make_mocks()
    with (
        patch(_EMBEDDING_PATH, return_value=mock_embed),
        patch(_QDRANT_PATH, return_value=mock_qdrant),
    ):
        results = retrieve_documents("trino", "How does row-level security work?")

    assert len(results) == 2
    assert results[0]["score"] == 0.91
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["collection_name"] == "trino"
    assert results[0]["tags"] == ["trino", "security"]


def test_retrieve_documents_passes_correct_args():
    mock_embed, mock_qdrant = _make_mocks()
    with (
        patch(_EMBEDDING_PATH, return_value=mock_embed),
        patch(_QDRANT_PATH, return_value=mock_qdrant),
    ):
        retrieve_documents("trino", "security query", limit=3)

    mock_embed.embed_text.assert_called_once_with("security query")
    mock_qdrant.search_similar_chunks.assert_called_once_with("trino", _FAKE_VECTOR, 3)


def test_retrieve_documents_empty_results():
    mock_embed, mock_qdrant = _make_mocks(results=[])
    with (
        patch(_EMBEDDING_PATH, return_value=mock_embed),
        patch(_QDRANT_PATH, return_value=mock_qdrant),
    ):
        results = retrieve_documents("trino", "query sem resultados")

    assert results == []


def test_retrieve_documents_collection_not_found_raises():
    mock_embed, mock_qdrant = _make_mocks(raise_value_error=True)
    with (
        patch(_EMBEDDING_PATH, return_value=mock_embed),
        patch(_QDRANT_PATH, return_value=mock_qdrant),
    ):
        with pytest.raises(ValueError, match="Collection não encontrada"):
            retrieve_documents("inexistente", "qualquer query")


def test_retrieve_documents_result_has_all_required_fields():
    mock_embed, mock_qdrant = _make_mocks()
    with (
        patch(_EMBEDDING_PATH, return_value=mock_embed),
        patch(_QDRANT_PATH, return_value=mock_qdrant),
    ):
        results = retrieve_documents("trino", "query")

    required = {
        "text",
        "score",
        "document_id",
        "filename",
        "collection_name",
        "page",
        "chunk_index",
        "tags",
        "source_type",
    }
    for result in results:
        assert required.issubset(result.keys())
