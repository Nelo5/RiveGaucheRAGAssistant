from app.services.qdrant_service import qdrant_service
from langchain_gigachat.chat_models import GigaChat
from app.core.config import settings


SYSTEM = '''Ты умный помощник магазина косметики "РивГош". Твоя задача - отвечать на вопросы клиентов на основе данных из контекста.
 Если в контексте недостаточно данных для ответа, скажи, что не можешь ответить на данный вопрос и предложи позвонить по 
 телефону бесплатной горячей линии: 8 (800) 234-44-60 . Отвечай сплошным текстом, где надо - списки.  НЕ ИСПОЛЬЗУЙ Markdown'''


class StubGigaChat:
    """Заглушка для GigaChat с тем же интерфейсом."""
    def __init__(self, credentials=None, verify_ssl_certs=False):
        # Параметры принимаются, но не используются
        pass

    def invoke(self, messages):
        # Возвращаем объект, имитирующий ответ LLM
        class StubResponse:
            content = "Это ответ-заглушка от искусственного интеллекта."
        return StubResponse()


class RAGService:
    def __init__(self):
        self.qdrant = qdrant_service
        self.llm = GigaChat(credentials=settings.GIGACHAT_CREDENTIALS, verify_ssl_certs=False)
        # self.llm = StubGigaChat(credentials=settings.GIGACHAT_CREDENTIALS, verify_ssl_certs=False)

    def initialize(self):
        self.qdrant.initialize()


    def ask(self, question: str, history: list = None):
        context_docs = self.qdrant.search(question)
        context_text = '\n\n'.join(doc.page_content for doc in context_docs)

        messages = [
            {'role': 'system', 'content': SYSTEM}
        ]

        if history:
            messages.extend(history)

        user_content = f"Контекст:\n{context_text}\n\nВопрос: {question}"
        messages.append({'role': 'user', 'content': user_content})
        return self.llm.invoke(messages).content

rag_service = RAGService()