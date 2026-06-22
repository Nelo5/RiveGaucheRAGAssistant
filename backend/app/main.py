from fastapi import FastAPI
from app.core.startup import lifespan
from app.api.routes import files, query, health, chats, auth
from app.api.routes import chats

from app.models import chat, message, user
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title='RAG System', lifespan=lifespan, openapi_version="3.0.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins= [origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(query.router)
app.include_router(health.router)
app.include_router(chats.router)
app.include_router(auth.router)