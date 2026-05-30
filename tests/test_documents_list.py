from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_CLIENT_PATH = "app.api.routes_documents._get_qdrant_client"

_SAMPLE_DOCS = [
    {
        "document_id": "doc-1",
        "filename": "trino-security.pdf",
        "collection_name": "trino",
        "chunks": 42,
        "tags": ["trino", "security"],
        "source_type": "official_docs",
    },
    {
        "document_id": "doc-2",
        "filename": "trino-connectors.pdf",
        "collection_name": "trino",
        "chunks": 18,
        "tags": [],
        "source_type": None,
    },
]


def _mock_client(docs=None, raise_value_error=False):
    mock = MagicMock()
    if raise_value_error:
        mock.list_documents.side_effect = ValueError("Collection não encontrada.")
    else:
        mock.list_documents.return_value = docs if docs is not None else _SAMPLE_DOCS
    return mock


def test_list_documents_returns_200():
    with patch(_CLIENT_PATH, return_value=_mock_client()):
        resp = client.get("/documents?collection_name=trino")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert body[0]["document_id"] == "doc-1"
    assert body[0]["chunks"] == 42
    assert body[0]["tags"] == ["trino", "security"]
    assert body[0]["source_type"] == "official_docs"


def test_list_documents_empty_collection_returns_empty_list():
    with patch(_CLIENT_PATH, return_value=_mock_client(docs=[])):
        resp = client.get("/documents?collection_name=empty-col")

    assert resp.status_code == 200
    assert resp.json() == []


def test_list_documents_collection_not_found_returns_404():
    with patch(_CLIENT_PATH, return_value=_mock_client(raise_value_error=True)):
        resp = client.get("/documents?collection_name=inexistente")

    assert resp.status_code == 404
    assert "Collection não encontrada" in resp.json()["detail"]


def test_list_documents_missing_collection_name_returns_422():
    resp = client.get("/documents")

    assert resp.status_code == 422


def test_list_documents_source_type_none_is_included():
    with patch(_CLIENT_PATH, return_value=_mock_client()):
        resp = client.get("/documents?collection_name=trino")

    body = resp.json()
    doc2 = next(d for d in body if d["document_id"] == "doc-2")
    assert doc2["source_type"] is None
    assert doc2["tags"] == []
