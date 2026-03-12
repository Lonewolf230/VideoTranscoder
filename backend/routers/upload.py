from fastapi import APIRouter
from controllers.upload_video import generate_multipart_upload,generate_presigned_url,complete_multipart_upload
from pydantic import BaseModel
from typing import List

class Part(BaseModel):
    PartNumber: int
    ETag: str
    
class CompleteUploadRequest(BaseModel):
    upload_id: str
    parts: List[Part]



upload_router = APIRouter()

@upload_router.post("/create-multipart-upload")
def create_multipart_upload():
    # Placeholder for video upload logic
    return generate_multipart_upload()

@upload_router.post("/part-url")
def generate_urls(part_number:int,upload_id:str):
    # print(f"Generating presigned URL for part {part_number} with upload ID {upload_id}")
    return generate_presigned_url(upload_id=upload_id,part_number=part_number)

@upload_router.post("/complete-multipart-upload")
def complete_upload(request: CompleteUploadRequest):
    # print(f"Completing multipart upload with ID {request.upload_id} and parts {request.parts}")
    parts_dict=[p.model_dump() for p in request.parts]
    return complete_multipart_upload(upload_id=request.upload_id, parts=parts_dict)