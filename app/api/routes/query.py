from fastapi import APIRouter, Depends, HTTPException
from openai import RateLimitError

from app.api.deps import get_current_user
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag_pipeline import run_query

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def query_docs(
    request: QueryRequest,
    _: dict = Depends(get_current_user),
) -> QueryResponse:
    try:
        return await run_query(request.question)
    except RateLimitError:
        raise HTTPException(status_code=429, detail="LLM rate limit exceeded — please retry later.")
