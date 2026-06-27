from fastapi import APIRouter

from app.db.vector_store import get_stats

router = APIRouter()


@router.get("/")
def health():
    return {"status": "ok", **get_stats()}
