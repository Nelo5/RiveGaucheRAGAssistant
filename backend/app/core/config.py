from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = 'RAG System'
    QDRANT_URL: str = 'http://qdrant:634'
    QDRANT_API_KEY: str = 'your_qdrant_api_key'
    COLLECTION_NAME: str = 'rivegauche_assistant'
    CORS_ALLOWED_ORIGINS: str 
    GIGACHAT_CREDENTIALS: str = ''
    DATABASE_URL:str = "postgresql://postgres:postgres@db:5432/ragdb"
    SECRET_KEY:str
    SPARSE_MODEL:str = "Qdrant/BM25"
    ALGORITHM:str = "HS256"    
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 60
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 150
    VECTOR_SIZE: int = 384
    class Config:
        env_file = '.env'

settings = Settings()