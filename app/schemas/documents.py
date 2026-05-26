from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    collection_name: str
    chunks: int
    status: str
    message: str
