from configs import s3config
from dotenv import load_dotenv
load_dotenv()
import os
import uuid

client=s3config.S3Config(
        access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region=os.getenv("AWS_REGION")
    )

def generate_multipart_upload():

    id=str(uuid.uuid4())
    file_key=f"videos/{id}"
    res = client.create_multipart_upload(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key
    )

    return res

# def generate_presigned_url(upload_id:str, part_number:int,file_key:str="videos/sample_video"):
    
#     res = client.generate_presigned_urls(
#         bucket_name=os.getenv("BUCKET_NAME"),
#         file_key=file_key,
#         upload_id=upload_id,
#         part_number=part_number
#     )

#     return res

def generate_all_presigned_urls(upload_id:str,total_parts:int,file_key:str):
    
    res = client.generate_all_presigned_urls(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key,
        upload_id=upload_id,
        total_parts=total_parts
    )

    return res

def complete_multipart_upload(upload_id:str, parts:list,file_key:str):
    
    res = client.complete_multipart_upload(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key,
        upload_id=upload_id,
        parts=parts
    )

    return res