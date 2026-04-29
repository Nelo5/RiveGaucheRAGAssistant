from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = 'RAG System'
    QDRANT_URL: str = 'http://qdrant:6333'
    COLLECTION_NAME: str = 'research-app'
    GIGACHAT_CREDENTIALS: str = 'ZmZlODJkYzAtMTAxMy00YzUzLWI4OWUtMWYzYWFiYjlhYTYzOmViOTY2OTdlLWJlNmItNDc3Yy04YWYzLTRlNTBlMzEzZjNkZg=='
    DATABASE_URL:str = "postgresql://postgres:postgres@db:5432/ragdb"
    SECRET_KEY:str  = "supersecretkey"
    ALGORITHM:str = "HS256"    
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 10080
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 150
    VECTOR_SIZE: int = 384
    class Config:
        env_file = '.env'

settings = Settings()