from fastapi import APIRouter,Depends
from fastapi import HTTPException
from controllers.upload_video import generate_multipart_upload,generate_all_presigned_urls,complete_multipart_upload
from pydantic import BaseModel
from typing import List
from configs.database import get_db
from utils.video import get_all_running_video_status

class Part(BaseModel):
    PartNumber: int
    ETag: str
    
class CompleteUploadRequest(BaseModel):
    upload_id: str
    parts: List[Part]
    file_key: str
    file_name: str



upload_router = APIRouter()

@upload_router.post("/create-multipart-upload")
def create_multipart_upload(file_name:str):
    # Placeholder for video upload logic
    try:
        return generate_multipart_upload(file_name=file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@upload_router.post("/part-url")
def generate_urls(total_parts:int,upload_id:str,file_key:str):
    # print(f"Generating presigned URL for part {part_number} with upload ID {upload_id}")
    try:
        return generate_all_presigned_urls(upload_id=upload_id, total_parts=total_parts,file_key=file_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@upload_router.post("/complete-multipart-upload")
def complete_upload(request: CompleteUploadRequest,db=Depends(get_db)):
    # print(f"Completing multipart upload with ID {request.upload_id} and parts {request.parts}")
    parts_dict=[p.model_dump() for p in request.parts]
    try:
        return complete_multipart_upload(upload_id=request.upload_id, parts=parts_dict,file_key=request.file_key,file_name=request.file_name,db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @upload_router.get("/process_status")
# def process_status(video_id:int,db=Depends(get_db)):
#     try:
#         return get_video_status(db=db,video_id=video_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@upload_router.get("/all-process-status")
def all_process_status(db=Depends(get_db)):
    try:
        return get_all_running_video_status(db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    