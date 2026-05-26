# Document routes — upload, list, and delete documents.

from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
async def upload_document():
    # TODO: ingest document into vector store
    raise NotImplementedError


@router.get("")
async def list_documents():
    # TODO: list documents from vector store
    raise NotImplementedError


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    # TODO: delete document from vector store
    raise NotImplementedError
