import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException
import logging

from config import COLLECTION_NAME
from models import QueryRequest, QueryResponse, UploadResponse
from ingestion import process_pdf
from retrieval import initialize, vector_store, graph

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG system...")
    initialize()
    yield
    logger.info("Shutting down...")

app = FastAPI(title="RAG System", lifespan=lifespan)

def check_stores():
    """Проверяет, что все компоненты инициализированы."""
    if vector_store is None or graph is None:
        raise HTTPException(
            status_code=503,
            detail="Система не готова. Попробуйте позже."
        )

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    check_stores()

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Поддерживаются только PDF‑файлы")

    content = await file.read()
    chunks = process_pdf(content, file.filename)
    vector_store.add_documents(chunks)

    return UploadResponse(
        status="ok",
        filename=file.filename,
        chunks_added=len(chunks)
    )

@app.post("/query", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    check_stores()

    try:
        result = graph.invoke({"question": req.question})
        return QueryResponse(answer=result["answer"])
    except Exception as e:
        raise HTTPException(500, f"Ошибка генерации ответа: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)