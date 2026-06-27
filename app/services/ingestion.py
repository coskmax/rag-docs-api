from app.db.vector_store import add_chunks
from app.utils.chunking import chunk_text
from app.utils.extractors import extract_text
from app.utils.logger import get_logger

logger = get_logger(__name__)


def ingest_document(content: bytes, filename: str) -> int:
    text = extract_text(content, filename)
    if not text.strip():
        raise ValueError(f"Could not extract text from '{filename}' — file may be empty or unreadable")
    chunks = chunk_text(text)
    logger.info(f"Ingesting '{filename}': {len(chunks)} chunks")
    return add_chunks(chunks, filename)
