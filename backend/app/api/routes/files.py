from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import file_service
from app.schemas.files import UploadResponse, FileInfo, DeleteResponse
from typing import List
from uuid import UUID


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

@router.post("", response_model=UploadResponse, responses={401: {"description": "Not authenticated"}})
async def upload_file(file: UploadFile = File(...)):
    return await file_service.upload_file(file)

@router.get("", response_model=List[FileInfo], responses={401: {"description": "Not authenticated"}})
def get_files():
    return file_service.list_files()

@router.get("/{file_id}", response_model=FileInfo, responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"}})
def get_file(file_id: UUID):
    return file_service.get_file(file_id)

@router.delete("/{file_id}", response_model=DeleteResponse, responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"}})
def delete_file(file_id: UUID):
    return file_service.delete_file(file_id)