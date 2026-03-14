from fastapi import APIRouter,Depends
from controllers.upload_video import generate_multipart_upload,generate_all_presigned_urls,complete_multipart_upload
from pydantic import BaseModel
from typing import List
from configs.database import get_db

class Part(BaseModel):
    PartNumber: int
    ETag: str
    
class CompleteUploadRequest(BaseModel):
    upload_id: str
    parts: List[Part]
    file_key: str



upload_router = APIRouter()

@upload_router.post("/create-multipart-upload")
def create_multipart_upload():
    # Placeholder for video upload logic
    return generate_multipart_upload()

@upload_router.post("/part-url")
def generate_urls(total_parts:int,upload_id:str,file_key:str):
    # print(f"Generating presigned URL for part {part_number} with upload ID {upload_id}")
    return generate_all_presigned_urls(upload_id=upload_id, total_parts=total_parts,file_key=file_key)

@upload_router.post("/complete-multipart-upload")
def complete_upload(request: CompleteUploadRequest,db=Depends(get_db)):
    # print(f"Completing multipart upload with ID {request.upload_id} and parts {request.parts}")
    parts_dict=[p.model_dump() for p in request.parts]
    return complete_multipart_upload(upload_id=request.upload_id, parts=parts_dict,file_key=request.file_key,db=db)