from configs.s3config import s3
from configs.sqs import sqs_client as sqs
from dotenv import load_dotenv

import json
load_dotenv()
import os
import uuid
from utils.video import create_video


def generate_multipart_upload(file_name:str):

    try:
        file_key = f"videos/{uuid.uuid4()}"
        res = s3.create_multipart_upload(
            bucket_name=os.getenv("BUCKET_NAME"),
            file_key=file_key,
            file_name=file_name
        )

        return res
    except Exception as e:
        print("Error creating multipart upload:", e)
        raise 

def generate_all_presigned_urls(upload_id:str,total_parts:int,file_key:str):
    
    try:
        res = s3.generate_all_presigned_urls(
            bucket_name=os.getenv("BUCKET_NAME"),
            file_key=file_key,
            upload_id=upload_id,
            total_parts=total_parts
        )

        return res
    except Exception as e:
        print("Error generating presigned URLs:", e)
        raise 

def complete_multipart_upload(upload_id:str, parts:list,file_key:str,db,file_name:str):
    
    try:   
        s3.complete_multipart_upload(
            bucket_name=os.getenv("BUCKET_NAME"),
            file_key=file_key,
            upload_id=upload_id,
            parts=parts
        )
    except Exception as e:
        print("Error completing multipart upload:", e)
        raise
    
    try:
        vid_res=create_video(db=db,file_key=file_key,file_name=file_name)
        message_body={
            "file_key":vid_res.file_key,
            "video_id":vid_res.id
        }
    except Exception as e:
        print("Could not create video record in database:", e)
        raise
        
    try:
        sqs.send_message(json.dumps(message_body))
    except Exception as e:
        print("Error sending message to SQS:", e)
        raise
        
    return message_body
