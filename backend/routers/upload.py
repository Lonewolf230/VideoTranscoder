from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from utils.auth import get_current_user
from configs.database import get_db
from controllers.upload_video import (
    generate_multipart_upload,
    generate_all_presigned_urls,
    complete_multipart_upload,
    generate_presigned_url
)
from utils.video import get_all_running_video_status, get_total_storage_for_user
from utils.auth import get_current_user
from exceptions import S3UploadError, DatabaseError, SQSMessageError,JWTTokenError


upload_router = APIRouter()


class Part(BaseModel):
    PartNumber: int
    ETag: str


class CompleteUploadRequest(BaseModel):
    upload_id: str
    parts: List[Part]
    file_key: str
    file_name: str
    file_size: int


@upload_router.post("/create-multipart-upload")
def create_upload(file_name: str,file_size:int,user_id=Depends(get_current_user),db=Depends(get_db)):
    if get_total_storage_for_user(user_id=user_id,db=db) + file_size > 5*1024*1024*1024:
        raise HTTPException(400, "Storage limit exceeded. You can only store up to 5GB of videos.")    
    try:
        return generate_multipart_upload(file_name)
    except S3UploadError as e:
        raise HTTPException(502, str(e))


@upload_router.post("/part-url")
def generate_urls(total_parts: int, upload_id: str, file_key: str):
    try:
        return generate_all_presigned_urls(upload_id, total_parts, file_key)
    except S3UploadError as e:
        raise HTTPException(502, str(e))


@upload_router.post("/complete-multipart-upload")
def complete_upload(request: CompleteUploadRequest, db=Depends(get_db),user_id=Depends(get_current_user)):
    try:
        parts_dict = [p.model_dump() for p in request.parts]

        return complete_multipart_upload(
            upload_id=request.upload_id,
            parts=parts_dict,
            file_key=request.file_key,
            file_name=request.file_name,
            file_size=request.file_size,
            user_id=user_id,
            db=db
        )

    except S3UploadError as e:
        raise HTTPException(502, str(e))
    
    except JWTTokenError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))

    except DatabaseError:
        raise HTTPException(500, "Database error : failed to create video record")

    except SQSMessageError:
        raise HTTPException(500, "Queue error : failed to send message to processing queue")

    except Exception:
        raise HTTPException(500, "Unexpected error")


@upload_router.get("/all-process-status")
def all_status(db=Depends(get_db)):
    try:
        return get_all_running_video_status(db)
    except DatabaseError:
        raise HTTPException(500, "Failed to fetch status")


@upload_router.get("/total-storage")
def total_storage(user_id=Depends(get_current_user), db=Depends(get_db)):
    try:
        print(user_id)
        storage = get_total_storage_for_user(user_id, db)
        print(f"Total storage used for user {user_id}: {storage} bytes")
        return {"storage_used": storage}
    except DatabaseError as e:
        print(f"Error calculating total storage for user {user_id}: {str(e)}")
        print(e.__cause__)
        raise HTTPException(500, "Failed to calculate storage")