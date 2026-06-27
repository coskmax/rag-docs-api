# 📄 Production-Ready RAG API for Document Q&A

A scalable backend API for querying documents using Retrieval-Augmented Generation (RAG).  
This system allows users to upload documents and ask natural language questions, returning accurate, cited answers.

---

## 🚀 Features

- 📂 Document ingestion (PDF support)
- 🔍 Semantic search using vector embeddings
- 🤖 LLM-powered question answering
- 📌 Source attribution (document + page references)
- 🔐 JWT authentication
- ⚡ FastAPI-based high-performance backend
- 📊 Structured logging and error handling
- 📖 Auto-generated API docs (Swagger)

---

## 🧠 Architecture Overview
Client → FastAPI → Auth Layer → Query Engine → Vector Store → LLM → Response


### Key Components

- **Ingestion Pipeline**
  - Extract text from PDFs
  - Chunk text into segments
  - Generate embeddings
  - Store in vector database

- **Query Pipeline**
  - Embed user query
  - Retrieve relevant chunks
  - Construct prompt with context
  - Generate answer via LLM

---

## 🛠 Tech Stack

- Backend: FastAPI
- Language: Python 3.11+
- LLM: OpenAI API
- Vector Store: FAISS
- Orchestration: LangChain
- Auth: JWT

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/rag-api
cd rag-api

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
