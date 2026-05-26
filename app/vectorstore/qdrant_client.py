from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

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

    def upsert_chunks(self, collection_name: str, points: list[dict]) -> None:
        if not self.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' não encontrada.")
        self._client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                for p in points
            ],
        )
