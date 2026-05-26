# Chat routes — receives user messages and returns agent responses.

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat():
    # TODO: invoke agentic graph
    raise NotImplementedError
