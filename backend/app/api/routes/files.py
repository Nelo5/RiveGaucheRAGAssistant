from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import file_service
from app.schemas.files import UploadResponse, FileInfo, DeleteResponse
from typing import List

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    return await file_service.upload_file(file)

@router.get("", response_model=List[FileInfo])
def get_files():
    return file_service.list_files()

@router.get("/{file_id}", response_model=FileInfo)
def get_file(file_id: str):
    return file_service.get_file(file_id)

@router.delete("/{file_id}", response_model=DeleteResponse)
def delete_file(file_id: str):
    return file_service.delete_file(file_id)