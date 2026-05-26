from uuid import uuid4

from app.ingestion.chunking import chunk_pages
from app.ingestion.embeddings import EmbeddingService
from app.ingestion.loaders import load_document
from app.vectorstore.qdrant_client import QdrantCollectionClient


class DocumentIngestionService:
    def __init__(self) -> None:
        self._embeddings = EmbeddingService()
        self._qdrant = QdrantCollectionClient()

    def ingest(
        self,
        file_path: str,
        filename: str,
        collection_name: str,
        tags: list[str],
        source_type: str | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> dict:
        document_id = str(uuid4())

        pages = load_document(file_path, filename=filename)
        texts = [p["text"] for p in pages if (p.get("text") or "").strip()]
        if not texts:
            raise ValueError("O documento não contém texto extraível.")

        chunks = chunk_pages(pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            raise ValueError("O chunking não gerou nenhum chunk a partir do documento.")

        chunk_texts = [c["text"] for c in chunks]
        vectors = self._embeddings.embed_texts(chunk_texts)

        points = [
            {
                "id": str(uuid4()),
                "vector": vector,
                "payload": {
                    "document_id": document_id,
                    "filename": filename,
                    "collection_name": collection_name,
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "tags": tags,
                    "source_type": source_type,
                },
            }
            for chunk, vector in zip(chunks, vectors)
        ]

        self._qdrant.upsert_chunks(collection_name, points)

        return {
            "document_id": document_id,
            "filename": filename,
            "collection_name": collection_name,
            "chunks": len(chunks),
        }
