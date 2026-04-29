from fastapi import FastAPI
from app.core.startup import lifespan
from app.api.routes import files, query, health, chats, auth
from app.api.routes import chats

from app.models import chat, message, user
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title='RAG System', lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(query.router)
app.include_router(health.router)
app.include_router(chats.router)
app.include_router(auth.router)