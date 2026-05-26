# Collection routes — manage Qdrant collections.

from fastapi import APIRouter

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("")
async def create_collection():
    # TODO: create a Qdrant collection
    raise NotImplementedError


@router.get("")
async def list_collections():
    # TODO: list Qdrant collections
    raise NotImplementedError


@router.delete("/{collection_name}")
async def delete_collection(collection_name: str):
    # TODO: delete a Qdrant collection
    raise NotImplementedError
