import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from app.ingestion.document_service import DocumentIngestionService
from app.ingestion.embeddings import EmbeddingError
from app.schemas.documents import (
    DocumentDeleteResponse,
    DocumentSummaryResponse,
    DocumentUploadResponse,
)
from app.vectorstore.qdrant_client import QdrantCollectionClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


def _get_qdrant_client() -> QdrantCollectionClient:
    return QdrantCollectionClient()


def _parse_tags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = Form(...),
    tags: str | None = Form(default=None),
    source_type: str | None = Form(default=None),
    chunk_size: int = Form(default=1000),
    chunk_overlap: int = Form(default=200),
):
    filename = file.filename or "upload"
    suffix = Path(filename).suffix or ""

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(await file.read())
        tmp.flush()
        tmp.close()

        result = DocumentIngestionService().ingest(
            file_path=tmp.name,
            filename=filename,
            collection_name=collection_name,
            tags=_parse_tags(tags),
            source_type=source_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except EmbeddingError as e:
        logger.exception("Falha na geração de embeddings para '%s'", filename)
        raise HTTPException(status_code=500, detail="Falha na geração de embeddings.") from e
    except ResponseHandlingException as e:
        logger.exception("Erro de conexão com Qdrant ao processar '%s'", filename)
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except UnexpectedResponse as e:
        logger.exception("Resposta inesperada do Qdrant ao processar '%s'", filename)
        if e.status_code and e.status_code < 500:
            raise HTTPException(
                status_code=400,
                detail=f"Qdrant rejeitou a operação: {e.reason_phrase}",
            ) from e
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        logger.exception("Erro inesperado ao processar documento '%s'", filename)
        raise HTTPException(
            status_code=500, detail="Erro inesperado ao processar o documento."
        ) from e
    finally:
        Path(tmp.name).unlink(missing_ok=True)

    return DocumentUploadResponse(
        document_id=result["document_id"],
        filename=result["filename"],
        collection_name=result["collection_name"],
        chunks=result["chunks"],
        status="indexed",
        message=f"Documento indexado com sucesso em '{collection_name}'.",
    )


@router.get("", response_model=list[DocumentSummaryResponse])
async def list_documents(
    collection_name: str = Query(...),
):
    try:
        docs = _get_qdrant_client().list_documents(collection_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Collection não encontrada.") from e
    except ResponseHandlingException as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except UnexpectedResponse as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        logger.exception("Erro ao listar documentos da collection '%s'", collection_name)
        raise HTTPException(status_code=500, detail="Erro interno ao listar documentos.") from e

    return [DocumentSummaryResponse(**d) for d in docs]


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    collection_name: str = Query(...),
):
    try:
        deleted = _get_qdrant_client().delete_document(collection_name, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Collection não encontrada.") from e
    except LookupError as e:
        raise HTTPException(
            status_code=404, detail="Documento não encontrado na collection informada."
        ) from e
    except ResponseHandlingException as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except UnexpectedResponse as e:
        raise HTTPException(status_code=503, detail="Qdrant indisponível.") from e
    except Exception as e:
        logger.exception(
            "Erro ao remover documento '%s' da collection '%s'", document_id, collection_name
        )
        raise HTTPException(status_code=500, detail="Erro interno ao remover documento.") from e

    return DocumentDeleteResponse(
        document_id=document_id,
        collection_name=collection_name,
        deleted_chunks=deleted,
        message="Documento removido com sucesso.",
    )
