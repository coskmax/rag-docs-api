from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str


class DocumentInfo(BaseModel):
    filename: str
    chunks: int
    uploaded_at: str


class BatchUploadResult(BaseModel):
    filename: str
    success: bool
    chunks_indexed: int | None = None
    message: str
