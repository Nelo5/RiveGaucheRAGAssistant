import tempfile
from pathlib import Path
from langchain_community.document_loaders.pdf import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

def process_pdf(file_content: bytes, filename: str) -> list:
    """
    Сохраняет PDF во временный файл, разбивает на чанки и возвращает список документов.
    """
    # Создаём временный файл с автоматическим удалением не сразу,
    # чтобы PDFPlumberLoader успел его прочитать
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = Path(tmp.name)

    try:
        loader = PDFPlumberLoader(str(tmp_path))
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = text_splitter.split_documents(docs)
        return chunks
    finally:
        # Удаляем временный файл после обработки
        if tmp_path.exists():
            tmp_path.unlink()