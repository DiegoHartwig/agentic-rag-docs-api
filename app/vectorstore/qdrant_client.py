from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import get_settings

_DISTANCE = Distance.COSINE


class QdrantCollectionClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._vector_size = settings.EMBEDDING_VECTOR_SIZE
        self._client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )

    def collection_exists(self, collection_name: str) -> bool:
        return self._client.collection_exists(collection_name)

    def create_collection(self, collection_name: str) -> dict:
        if self.collection_exists(collection_name):
            return {
                "collection_name": collection_name,
                "status": "exists",
                "message": f"Collection '{collection_name}' já existe.",
            }
        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=self._vector_size, distance=_DISTANCE),
        )
        return {
            "collection_name": collection_name,
            "status": "created",
            "message": f"Collection '{collection_name}' criada com sucesso.",
        }

    def list_collections(self) -> list[str]:
        result = self._client.get_collections()
        return [c.name for c in result.collections]

    def delete_collection(self, collection_name: str) -> dict:
        if not self.collection_exists(collection_name):
            return {
                "collection_name": collection_name,
                "status": "not_found",
                "message": f"Collection '{collection_name}' não encontrada.",
            }
        self._client.delete_collection(collection_name)
        return {
            "collection_name": collection_name,
            "status": "deleted",
            "message": f"Collection '{collection_name}' removida com sucesso.",
        }

    def list_documents(self, collection_name: str) -> list[dict]:
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' não encontrada.")

        docs: dict[str, dict] = {}
        offset = None
        while True:
            records, next_offset = self._client.scroll(
                collection_name=collection_name,
                with_payload=True,
                with_vectors=False,
                limit=100,
                offset=offset,
            )
            for record in records:
                payload = record.payload or {}
                doc_id = payload.get("document_id")
                if not doc_id:
                    continue
                if doc_id not in docs:
                    docs[doc_id] = {
                        "document_id": doc_id,
                        "filename": payload.get("filename", ""),
                        "collection_name": payload.get("collection_name", collection_name),
                        "tags": payload.get("tags", []),
                        "source_type": payload.get("source_type"),
                        "chunks": 0,
                    }
                docs[doc_id]["chunks"] += 1
            if next_offset is None:
                break
            offset = next_offset

        return list(docs.values())

    def delete_document(self, collection_name: str, document_id: str) -> int:
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' não encontrada.")

        doc_filter = Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        )

        point_ids: list = []
        offset = None
        while True:
            records, next_offset = self._client.scroll(
                collection_name=collection_name,
                scroll_filter=doc_filter,
                with_payload=False,
                with_vectors=False,
                limit=100,
                offset=offset,
            )
            point_ids.extend(r.id for r in records)
            if next_offset is None:
                break
            offset = next_offset

        if not point_ids:
            raise LookupError(
                f"Documento '{document_id}' não encontrado na collection '{collection_name}'."
            )

        self._client.delete(
            collection_name=collection_name,
            points_selector=point_ids,
        )
        return len(point_ids)

    def search_similar_chunks(
        self, collection_name: str, query_vector: list[float], limit: int = 5
    ) -> list[dict]:
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' não encontrada.")

        hits = self._client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
        )
        results = []
        for hit in hits:
            payload = hit.payload or {}
            results.append(
                {
                    "text": payload.get("text", ""),
                    "score": hit.score,
                    "document_id": payload.get("document_id", ""),
                    "filename": payload.get("filename", ""),
                    "collection_name": payload.get("collection_name", collection_name),
                    "page": payload.get("page"),
                    "chunk_index": payload.get("chunk_index"),
                    "tags": payload.get("tags", []),
                    "source_type": payload.get("source_type"),
                }
            )
        return results

    def upsert_chunks(self, collection_name: str, points: list[dict]) -> None:
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' não encontrada.")
        self._client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"]) for p in points
            ],
        )
