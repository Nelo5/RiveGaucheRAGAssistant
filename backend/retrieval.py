import logging
from typing import List
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from langchain_gigachat.chat_models import GigaChat
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from config import QDRANT_URL, COLLECTION_NAME, VECTOR_SIZE, GIGACHAT_CREDENTIALS, SYSTEM_TEMPLATE, HUMAN_TEMPLATE

logger = logging.getLogger(__name__)

class RAGState(TypedDict):
    question: str
    context: List[any]
    answer: str

embeddings: FastEmbedEmbeddings = None
bm25_model: FastEmbedSparse = None
client: QdrantClient = None
vector_store: QdrantVectorStore = None
llm: GigaChat = None
graph = None

def initialize():
    global embeddings, bm25_model, client, vector_store, llm, graph

    try:
        logger.info("Initializing embeddings...")
        embeddings = FastEmbedEmbeddings()
        bm25_model = FastEmbedSparse(model_name="Qdrant/BM25")

        logger.info("Connecting to Qdrant at %s", QDRANT_URL)
        client = QdrantClient(url=QDRANT_URL)
        if not client.collection_exists(COLLECTION_NAME):
            logger.info("Creating collection '%s'", COLLECTION_NAME)
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={"Dense": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE, on_disk=True)},
                sparse_vectors_config={"Sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))}
            )

        logger.info("Building QdrantVectorStore (hybrid)...")
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
            sparse_embedding=bm25_model,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="Dense",
            sparse_vector_name="Sparse",
        )

        logger.info("Initializing GigaChat LLM...")
        llm = GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False)

        # Функции графа
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
        logger.info("Initialization complete.")

    except Exception as e:
        logger.error("Initialization failed: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to initialize RAG system: {e}")