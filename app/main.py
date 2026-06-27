from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, documents, health, query
from app.db.database import create_tables
from app.db.vector_store import load_from_disk


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    load_from_disk()
    yield


app = FastAPI(
    title="RAG Docs API",
    version="0.1.0",
    description="Retrieval-Augmented Generation API for document Q&A",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(health.router, prefix="/health", tags=["Health"])
