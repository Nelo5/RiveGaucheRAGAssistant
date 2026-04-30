from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from app.core.config import settings

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.embeddings = FastEmbedEmbeddings()
        self.sparse = FastEmbedSparse(model_name='Qdrant/BM25')
        self.store = None

    def initialize(self):
        if not self.client.collection_exists(settings.COLLECTION_NAME):
            self.client.create_collection(
                collection_name=settings.COLLECTION_NAME,
                vectors_config={
                    'Dense': VectorParams(size=settings.VECTOR_SIZE, distance=Distance.COSINE, on_disk=True)
                },
                sparse_vectors_config={
                    'Sparse': SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                }
            )
        self.store = QdrantVectorStore(
            client=self.client,
            collection_name=settings.COLLECTION_NAME,
            embedding=self.embeddings,
            sparse_embedding=self.sparse,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name='Dense',
            sparse_vector_name='Sparse'
        )

    def add_documents(self, docs):
        self.store.add_documents(docs)

    def search(self, question: str):
        return self.store.max_marginal_relevance_search(question)
    
qdrant_service = QdrantService()