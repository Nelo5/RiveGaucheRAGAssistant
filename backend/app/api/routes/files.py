from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.services.file_service import file_service
from app.schemas.files import UploadResponse, FileInfo, DeleteResponse
from typing import List
from uuid import UUID
from app.core.deps import require_admin


router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

@router.post("", response_model=UploadResponse, responses={401: {"description": "Not authenticated"}, 400: {"description": "Malformed multipart request"},403: {"detail": "Admin privileges required"}})
async def upload_file(file: UploadFile = File(...), current_user=Depends(require_admin)):
    return await file_service.upload_file(file)

@router.get("", response_model=List[FileInfo], responses={401: {"description": "Not authenticated"},403: {"detail": "Admin privileges required"}})
def get_files(current_user=Depends(require_admin)):
    return file_service.list_files()

@router.get("/{file_id}", response_model=FileInfo, responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"},403: {"detail": "Admin privileges required"}})
def get_file(file_id: UUID, current_user=Depends(require_admin)):
    return file_service.get_file(file_id)

@router.delete("/{file_id}", response_model=DeleteResponse, responses={401: {"description": "Not authenticated"}, 404: {"description": "File not found"},403: {"detail": "Admin privileges required"}})
def delete_file(file_id: UUID, current_user=Depends(require_admin)):
    return file_service.delete_file(file_id)