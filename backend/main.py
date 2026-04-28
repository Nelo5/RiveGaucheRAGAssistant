import os
import uuid
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uvicorn

# LangChain
from langchain_community.document_loaders.pdf import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams

# LLM (GigaChat)
from langchain_gigachat.chat_models import GigaChat
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

load_dotenv()

# ------------------------------------------------------------
# Конфигурация
COLLECTION_NAME = "research-app"
QDRANT_URL = "http://localhost:6333"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 150
VECTOR_SIZE = 384          # размерность FastEmbed (bge‑small‑en)
# ------------------------------------------------------------

# Состояние RAG-графа
class RAGState(TypedDict):
    question: str
    context: List[any]      # фактически List[langchain_core.documents.Document]
    answer: str

# Системный и пользовательский промпты
SYSTEM_TEMPLATE = """
You are an expert QA Assistant who answers questions using only the provided context as your source of information.
If the question is not from the provided context, say `I don't know. Not enough information received.`
"""

HUMAN_TEMPLATE = """
We have provided context information below.

CONTEXT: {context_str}
---------------------
Given this information, please answer the question: {query}
---------------------
If the question is not from the provided context, say `I don't know. Not enough information received.`
"""

# ------------------------------------------------------------
# Глобальные объекты (инициализируются при старте приложения)
embeddings: FastEmbedEmbeddings = None
bm25_model: FastEmbedSparse = None
client: QdrantClient = None
vector_store: QdrantVectorStore = None
llm: GigaChat = None
graph = None
# ------------------------------------------------------------

def init_components():
    """Инициализация эмбеддингов, Qdrant, LLM и графа."""
    global embeddings, bm25_model, client, vector_store, llm, graph

    # Эмбеддинги
    embeddings = FastEmbedEmbeddings()
    bm25_model = FastEmbedSparse(model_name="Qdrant/BM25")

    # Qdrant клиент и коллекция
    client = QdrantClient(url=QDRANT_URL)
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"Dense": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE, on_disk=True)},
            sparse_vectors_config={"Sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))}
        )

    # QdrantVectorStore с гибридным поиском
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
        sparse_embedding=bm25_model,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name="Dense",
        sparse_vector_name="Sparse",
    )

    # LLM (GigaChat)
    credentials = os.environ.get("GIGACHAT_CREDENTIALS")
    if not credentials:
        raise RuntimeError("GIGACHAT_CREDENTIALS not set in environment")
    llm = GigaChat(credentials=credentials, verify_ssl_certs=False)

    # Граф RAG
    def search(state: RAGState):
        retrieved_docs = vector_store.max_marginal_relevance_search(state["question"])
        return {"context": retrieved_docs}

    def generate(state: RAGState):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = [
            {"role": "system", "content": SYSTEM_TEMPLATE},
            {"role": "user", "content": HUMAN_TEMPLATE.format(context_str=docs_content, query=state["question"])},
        ]
        response = llm.invoke(messages)
        return {"answer": response.content}

    graph_builder = StateGraph(RAGState)
    graph_builder.add_sequence([search, generate])
    graph_builder.add_edge(START, "search")
    graph_builder.add_edge("search", "generate")
    graph_builder.add_edge("generate", END)
    graph = graph_builder.compile()

# ------------------------------------------------------------
# FastAPI приложение
app = FastAPI(title="RAG System")

@app.on_event("startup")
async def startup_event():
    init_components()

# ---------- Модели запросов/ответов ----------
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str


# ---------- Эндпоинты ----------
import tempfile
from pathlib import Path

@app.post("/upload", summary="Загрузить PDF в базу знаний")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Поддерживаются только PDF‑файлы")

    # Создаём временный файл с расширением .pdf
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        # Загрузка и разделение
        loader = PDFPlumberLoader(str(tmp_path))
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = text_splitter.split_documents(docs)

        # Добавление в векторное хранилище
        vector_store.add_documents(chunks)

        return {
            "status": "ok",
            "filename": file.filename,
            "chunks_added": len(chunks),
        }
    except Exception as e:
        raise HTTPException(500, f"Ошибка обработки файла: {e}")
    finally:
        # Удаляем временный файл
        if tmp_path.exists():
            tmp_path.unlink()

@app.post("/query", response_model=QueryResponse, summary="Задать вопрос RAG‑системе")
async def ask_question(req: QueryRequest):
    """
    Выполняет поиск релевантных чанков и генерирует ответ с помощью GigaChat.
    """
    if graph is None:
        raise HTTPException(500, "Система ещё не инициализирована")
    try:
        result = graph.invoke({"question": req.question})
        return QueryResponse(answer=result["answer"])
    except Exception as e:
        raise HTTPException(500, f"Ошибка генерации ответа: {e}")

# ---------- Запуск ----------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)