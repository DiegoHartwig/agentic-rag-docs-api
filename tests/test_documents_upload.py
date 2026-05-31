from io import BytesIO
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_INGEST_PATH = "app.api.routes_documents.DocumentIngestionService"


def _mock_ingest(filename="doc.txt", collection="minha-col", chunks=3):
    mock_service = MagicMock()
    mock_service.ingest.return_value = {
        "document_id": "fake-uuid",
        "filename": filename,
        "collection_name": collection,
        "chunks": chunks,
    }
    return mock_service


def test_upload_txt_returns_200():
    with patch(_INGEST_PATH, return_value=_mock_ingest()):
        resp = client.post(
            "/documents/upload",
            data={"collection_name": "minha-col"},
            files={"file": ("doc.txt", BytesIO(b"hello world"), "text/plain")},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "indexed"
    assert body["chunks"] == 3
    assert body["document_id"] == "fake-uuid"


def test_upload_parses_comma_separated_tags():
    captured = {}

    def fake_init(self):
        self.ingest = lambda **kw: (
            captured.update(kw)
            or {
                "document_id": "x",
                "filename": kw["filename"],
                "collection_name": kw["collection_name"],
                "chunks": 1,
            }
        )

    with patch(_INGEST_PATH, new=type("S", (), {"__init__": fake_init})):
        client.post(
            "/documents/upload",
            data={"collection_name": "col", "tags": "trino, dbt, spark"},
            files={"file": ("f.txt", BytesIO(b"texto"), "text/plain")},
        )

    assert captured.get("tags") == ["trino", "dbt", "spark"]


def test_upload_value_error_returns_400():
    mock_service = MagicMock()
    mock_service.ingest.side_effect = ValueError("O documento não contém texto extraível.")

    with patch(_INGEST_PATH, return_value=mock_service):
        resp = client.post(
            "/documents/upload",
            data={"collection_name": "col"},
            files={"file": ("empty.txt", BytesIO(b""), "text/plain")},
        )

    assert resp.status_code == 400
    assert "texto extraível" in resp.json()["detail"]
