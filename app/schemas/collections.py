from pydantic import BaseModel, Field


class CollectionCreateRequest(BaseModel):
    collection_name: str = Field(min_length=2, pattern=r"^[a-z0-9_-]+$")
    description: str | None = None


class CollectionResponse(BaseModel):
    collection_name: str
    status: str
    message: str


class CollectionListResponse(BaseModel):
    collections: list[str]
