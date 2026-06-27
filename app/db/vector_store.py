import json
from datetime import datetime, timezone
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.utils.logger import get_logger

logger = get_logger(__name__)

_model = SentenceTransformer("all-MiniLM-L6-v2")
_index: faiss.IndexFlatL2 | None = None
_chunks: list[str] = []
_chunk_sources: list[str] = []  # parallel to _chunks — which document each chunk came from
_documents: dict[str, dict] = {}  # filename -> {chunks, uploaded_at}

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension


def _data_dir() -> Path:
    from app.core.config import settings
    path = Path(settings.DATA_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_index() -> faiss.IndexFlatL2:
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(EMBEDDING_DIM)
    return _index


def load_from_disk() -> None:
    """Load persisted index and metadata from disk. Called once on startup."""
    global _index, _chunks, _chunk_sources, _documents
    idx_path = _data_dir() / "faiss.index"
    meta_path = _data_dir() / "meta.json"
    if idx_path.exists() and meta_path.exists():
        _index = faiss.read_index(str(idx_path))
        with open(meta_path) as f:
            meta = json.load(f)
        _chunks = meta["chunks"]
        _chunk_sources = meta["chunk_sources"]
        _documents = meta["documents"]
        logger.info(f"Loaded index: {_index.ntotal} vectors across {len(_documents)} document(s)")
    else:
        _index = faiss.IndexFlatL2(EMBEDDING_DIM)
        logger.info("No persisted index found — starting fresh")


def _save_to_disk() -> None:
    faiss.write_index(_get_index(), str(_data_dir() / "faiss.index"))
    with open(_data_dir() / "meta.json", "w") as f:
        json.dump({"chunks": _chunks, "chunk_sources": _chunk_sources, "documents": _documents}, f)


def add_chunks(chunks: list[str], filename: str) -> int:
    global _chunks, _chunk_sources, _documents
    vectors = _model.encode(chunks, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    _get_index().add(vectors)
    _chunks.extend(chunks)
    _chunk_sources.extend([filename] * len(chunks))
    _documents[filename] = {
        "chunks": len(chunks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_to_disk()
    return len(chunks)


def search(query: str, k: int = 4) -> list[dict]:
    index = _get_index()
    if index.ntotal == 0:
        return []
    vector = _model.encode(query, convert_to_numpy=True).astype(np.float32).reshape(1, -1)
    distances, indices = index.search(vector, k)
    results = []
    for dist, i in zip(distances[0], indices[0]):
        if i < len(_chunks):
            results.append({
                "text": _chunks[i],
                "document": _chunk_sources[i],
                "score": float(np.exp(-dist)),  # L2 distance → 0–1 similarity score
            })
    return results


def delete_document(filename: str) -> bool:
    """Remove a document and rebuild the index without it. Returns False if not found."""
    global _index, _chunks, _chunk_sources, _documents
    if filename not in _documents:
        return False
    # Filter out all chunks belonging to this document
    remaining = [(c, s) for c, s in zip(_chunks, _chunk_sources) if s != filename]
    _chunks = [c for c, _ in remaining]
    _chunk_sources = [s for _, s in remaining]
    del _documents[filename]
    # Rebuild the FAISS index from remaining chunks
    _index = faiss.IndexFlatL2(EMBEDDING_DIM)
    if _chunks:
        vectors = _model.encode(_chunks, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
        _index.add(vectors)
    logger.info(f"Deleted '{filename}', rebuilt index with {_index.ntotal} vectors")
    _save_to_disk()
    return True


def get_documents() -> dict[str, dict]:
    return _documents.copy()


def get_stats() -> dict:
    return {"documents_indexed": len(_documents), "vectors_indexed": _get_index().ntotal}


def reset() -> None:
    """Clear the entire index. Useful for testing."""
    global _index, _chunks, _chunk_sources, _documents
    _index = faiss.IndexFlatL2(EMBEDDING_DIM)
    _chunks = []
    _chunk_sources = []
    _documents = {}
    _save_to_disk()
