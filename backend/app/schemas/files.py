from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import List

class UploadResponse(BaseModel):
    status: str
    file_id: UUID
    filename: str
    chunks_added: int

class FileInfo(BaseModel):
    file_id: UUID
    filename: str
    uploaded_at: str 
    chunks: int

class DeleteResponse(BaseModel):
    status: str
    message: str