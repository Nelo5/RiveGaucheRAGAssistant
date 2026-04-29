from contextlib import asynccontextmanager
from app.services.rag_service import rag_service
from app.services.qdrant_service import qdrant_service


@asynccontextmanager
async def lifespan(app):
    qdrant_service.initialize()
    rag_service.initialize()
    yield