from pydantic import BaseModel
from typing import List

class UploadResponse(BaseModel):
    status: str
    file_id: str
    filename: str
    chunks_added: int

class FileInfo(BaseModel):
    file_id: str
    filename: str
    uploaded_at: str 
    chunks: int

class DeleteResponse(BaseModel):
    status: str
    message: str