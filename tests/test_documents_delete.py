from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_CLIENT_PATH = "app.api.routes_documents._get_qdrant_client"


def _mock_client(deleted_chunks=42, raise_value_error=False, raise_lookup_error=False):
    mock = MagicMock()
    if raise_value_error:
        mock.delete_document.side_effect = ValueError("Collection não encontrada.")
    elif raise_lookup_error:
        mock.delete_document.side_effect = LookupError("Documento não encontrado.")
    else:
        mock.delete_document.return_value = deleted_chunks
    return mock


def test_delete_document_returns_200():
    with patch(_CLIENT_PATH, return_value=_mock_client(deleted_chunks=42)):
        resp = client.delete("/documents/abc-123?collection_name=trino")

    assert resp.status_code == 200
    body = resp.json()
    assert body["document_id"] == "abc-123"
    assert body["collection_name"] == "trino"
    assert body["deleted_chunks"] == 42
    assert body["message"] == "Documento removido com sucesso."


def test_delete_document_calls_client_with_correct_args():
    mock = _mock_client()
    with patch(_CLIENT_PATH, return_value=mock):
        client.delete("/documents/doc-999?collection_name=minha-col")

    mock.delete_document.assert_called_once_with("minha-col", "doc-999")


def test_delete_document_collection_not_found_returns_404():
    with patch(_CLIENT_PATH, return_value=_mock_client(raise_value_error=True)):
        resp = client.delete("/documents/abc-123?collection_name=inexistente")

    assert resp.status_code == 404
    assert "Collection não encontrada" in resp.json()["detail"]


def test_delete_document_not_found_returns_404():
    with patch(_CLIENT_PATH, return_value=_mock_client(raise_lookup_error=True)):
        resp = client.delete("/documents/inexistente?collection_name=trino")

    assert resp.status_code == 404
    assert "Documento não encontrado" in resp.json()["detail"]


def test_delete_document_missing_collection_name_returns_422():
    resp = client.delete("/documents/abc-123")

    assert resp.status_code == 422
