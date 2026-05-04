import uuid
from datetime import datetime
from pathlib import Path
import tempfile
from app.core.config import settings

from fastapi import UploadFile, HTTPException
from qdrant_client import models

from app.services.qdrant_service import qdrant_service
from langchain_community.document_loaders.pdf import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings




class FileService:

    def load_and_split(self, path: str):
        docs = PDFPlumberLoader(path).load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        return splitter.split_documents(docs)

    async def upload_file(self, file: UploadFile):

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Поддерживаются только PDF")

        file_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            temp_path = Path(tmp.name)

        try:
            chunks = self.load_and_split(str(temp_path))

            for chunk in chunks:
                chunk.metadata["file_id"] = file_id
                chunk.metadata["filename"] = file.filename
                chunk.metadata["uploaded_at"] = datetime.utcnow().isoformat()

            qdrant_service.add_documents(chunks)

            return {
                "status": "success",
                "file_id": file_id,
                "filename": file.filename,
                "chunks_added": len(chunks)
            }

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def list_files(self):

        points, _ = qdrant_service.client.scroll(
            collection_name=settings.COLLECTION_NAME,
            with_payload=True,
            limit=10000
        )

        files = {}

        for point in points:

            meta = point.payload.get("metadata", {})

            file_id = meta.get("file_id")
            filename = meta.get("filename")
            uploaded_at = meta.get("uploaded_at")

            if not file_id:
                continue

            if file_id not in files:
                files[file_id] = {
                    "file_id": file_id,
                    "filename": filename,
                    "uploaded_at": uploaded_at,
                    "chunks": 0
                }

            files[file_id]["chunks"] += 1

        return list(files.values())

    def get_file(self, file_id: str):

        points, _ = qdrant_service.client.scroll(
            collection_name=settings.COLLECTION_NAME,
            with_payload=True,
            limit=10000,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.file_id",
                        match=models.MatchValue(value=file_id)
                    )
                ]
            )
        )

        if not points:
            raise HTTPException(404, "Файл не найден")

        first = points[0].payload["metadata"]

        return {
            "file_id": file_id,
            "filename": first["filename"],
            "uploaded_at": first["uploaded_at"],
            "chunks": len(points)
        }
    
    def delete_file(self, file_id: str):

        self.get_file(file_id)

        qdrant_service.client.delete(
            collection_name=settings.COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.file_id",
                            match=models.MatchValue(value=file_id)
                        )
                    ]
                )
            )
        )

        return {
            "status": "success",
            "message": f"Файл {file_id} удалён"
        }


file_service = FileService()