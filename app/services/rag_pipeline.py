from fastapi import HTTPException, status

from app.services.llm import generate_answer
from app.services.retrieval import retrieve_chunks
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def run_query(question: str) -> dict:
    results = retrieve_chunks(question)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No documents have been indexed yet. Upload a PDF first.",
        )
    context_chunks = [r["text"] for r in results]
    confidence = round(sum(r["score"] for r in results) / len(results), 3)
    logger.info(f"Retrieved {len(results)} chunks, avg confidence={confidence}")
    answer = await generate_answer(question, context_chunks)
    return {
        "answer": answer,
        "sources": results,
        "confidence": confidence,
    }
