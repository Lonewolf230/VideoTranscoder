from configs.s3config import s3
from configs.sqs import sqs_client as sqs
from dotenv import load_dotenv

import json
load_dotenv()
import os
import uuid
from utils.video import create_video


def generate_multipart_upload():

    id=str(uuid.uuid4())
    file_key=f"videos/{id}"
    res = s3.create_multipart_upload(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key
    )

    return res

def generate_all_presigned_urls(upload_id:str,total_parts:int,file_key:str):
    
    res = s3.generate_all_presigned_urls(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key,
        upload_id=upload_id,
        total_parts=total_parts
    )

    return res

def complete_multipart_upload(upload_id:str, parts:list,file_key:str,db):
    
    res = s3.complete_multipart_upload(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key,
        upload_id=upload_id,
        parts=parts
    )
    vid_res=create_video(db=db,file_key=file_key)
    message_body={
        "file_key":vid_res.file_key,
        "video_id":vid_res.id
    }
    
    sqs.send_message(json.dumps(message_body))
    
    return res
