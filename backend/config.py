import os
from dotenv import load_dotenv

load_dotenv()

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "research-app"

# Чанкинг
CHUNK_SIZE = 1300
CHUNK_OVERLAP = 200

# Эмбеддинги
VECTOR_SIZE = 384          # размерность FastEmbed (bge-small-en)

# LLM (GigaChat)
GIGACHAT_CREDENTIALS = os.environ.get("GIGACHAT_CREDENTIALS")
if not GIGACHAT_CREDENTIALS:
    raise RuntimeError("GIGACHAT_CREDENTIALS not set in environment")

# Промпты
SYSTEM_TEMPLATE = """Ты — бот поддержки сети магазинов "Магнит", который отвечает на вопросы, используя предоставленный контекст.
Если контекста недостаточно для ответа, честно скажи, что не знаешь.
"""

HUMAN_TEMPLATE = """
У нас есть такой контекст.

КОНТЕКСТ: {context_str}
---------------------
Учитывая данную информацию, ответь на вопрос: {query}
---------------------
Если контекста недостаточно для ответа, честно скажи, что не знаешь.
"""