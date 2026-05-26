from fastapi import APIRouter, HTTPException
from qdrant_client.http.exceptions import UnexpectedResponse

from app.schemas.collections import (
    CollectionCreateRequest,
    CollectionListResponse,
    CollectionResponse,
)
from app.vectorstore.qdrant_client import QdrantCollectionClient

router = APIRouter(prefix="/collections", tags=["Collections"])


def _get_client() -> QdrantCollectionClient:
    return QdrantCollectionClient()


@router.post("", response_model=CollectionResponse)
async def create_collection(body: CollectionCreateRequest):
    try:
        result = _get_client().create_collection(body.collection_name)
        return result
    except UnexpectedResponse as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao criar collection.") from e


@router.get("", response_model=CollectionListResponse)
async def list_collections():
    try:
        names = _get_client().list_collections()
        return CollectionListResponse(collections=names)
    except UnexpectedResponse as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao listar collections.") from e


@router.delete("/{collection_name}", response_model=CollectionResponse)
async def delete_collection(collection_name: str):
    try:
        client = _get_client()
        result = client.delete_collection(collection_name)
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except UnexpectedResponse as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao remover collection.") from e
