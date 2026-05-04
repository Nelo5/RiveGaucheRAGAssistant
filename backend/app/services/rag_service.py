from app.services.qdrant_service import qdrant_service
from langchain_gigachat.chat_models import GigaChat
from app.core.config import settings


SYSTEM = '''Ты умный помощник магазина "Магнит". Твоя задача - отвечать на вопросы клиентов на основе данных из контекста.
 Если в контексте недостаточно данных для ответа, скажи, что не можешь ответить на данный вопрос. Отвечай простым текстом, не в формате Markdown.'''


class RAGService:
    def __init__(self):
        self.qdrant = qdrant_service
        self.llm = GigaChat(credentials=settings.GIGACHAT_CREDENTIALS, verify_ssl_certs=False)

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