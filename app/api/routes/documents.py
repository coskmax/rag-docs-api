from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from app.api.deps import get_current_user
from app.db.vector_store import delete_document, get_documents, reset
from app.schemas.document import BatchUploadResult, DocumentInfo, DocumentUploadResponse
from app.services.ingestion import ingest_document
from app.utils.extractors import SUPPORTED_EXTENSIONS

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _validate_and_read_file(file: UploadFile, content: bytes) -> str | None:
    """Returns an error message if the file is invalid, None if ok."""
    if not file.filename or Path(file.filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        return f"Unsupported file type. Supported: {supported}"
    if len(content) > MAX_FILE_SIZE:
        return "File exceeds the 10 MB limit"
    return None


@router.delete("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_documents(_: dict = Depends(get_current_user)) -> None:
    """Remove all documents and clear the index."""
    reset()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(filename: str = Query(...), _: dict = Depends(get_current_user)) -> None:
    if not delete_document(filename):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{filename}' not found")


@router.get("/", response_model=list[DocumentInfo])
def list_documents(_: dict = Depends(get_current_user)) -> list[DocumentInfo]:
    return [
        DocumentInfo(filename=name, **meta)
        for name, meta in get_documents().items()
    ]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_user),
) -> DocumentUploadResponse:
    content = await file.read()
    error = _validate_and_read_file(file, content)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    try:
        chunks_indexed = ingest_document(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return DocumentUploadResponse(
        filename=file.filename,
        chunks_indexed=chunks_indexed,
        message="Document indexed successfully",
    )


@router.post("/upload/batch", response_model=list[BatchUploadResult])
async def upload_documents(
    files: list[UploadFile] = File(...),
    _: dict = Depends(get_current_user),
) -> list[BatchUploadResult]:
    results = []
    for file in files:
        content = await file.read()
        error = _validate_and_read_file(file, content)
        if error:
            results.append(BatchUploadResult(filename=file.filename or "unknown", success=False, message=error))
            continue
        try:
            chunks_indexed = ingest_document(content, file.filename)
            results.append(BatchUploadResult(
                filename=file.filename,
                success=True,
                chunks_indexed=chunks_indexed,
                message="Indexed successfully",
            ))
        except ValueError as exc:
            results.append(BatchUploadResult(filename=file.filename, success=False, message=str(exc)))
    return results
