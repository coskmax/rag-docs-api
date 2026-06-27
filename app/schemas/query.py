from pydantic import BaseModel, Field


class Source(BaseModel):
    text: str
    document: str
    score: float


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: float
