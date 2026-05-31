from app.ingestion.embeddings import EmbeddingService
from app.vectorstore.qdrant_client import QdrantCollectionClient


def retrieve_documents(
    collection_name: str,
    query: str,
    limit: int = 5,
) -> list[dict]:
    query_vector = EmbeddingService().embed_text(query)
    return QdrantCollectionClient().search_similar_chunks(collection_name, query_vector, limit)
