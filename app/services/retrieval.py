from app.db.vector_store import search


def retrieve_chunks(query: str) -> list[dict]:
    return search(query)
