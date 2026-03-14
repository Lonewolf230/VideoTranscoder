import boto3
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from configs.database import get_db
from utils.video import update_video_status
load_dotenv()

class S3Config:

    def __init__(self):
        self.s3=boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

        
    def create_multipart_upload(self, bucket_name: str, file_key: str):
        

        response = self.s3.create_multipart_upload(
            Bucket=bucket_name,
            Key=file_key,
            ContentType='video/mp4'
        )

        return {
            "upload_id": response['UploadId'],
            "file_key": file_key
        }
    
    def generate_presigned_url(self, bucket_name: str, file_key: str, upload_id: str, part_number: int):
        
        url = self.s3.generate_presigned_url(
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket_name,
                'Key': file_key,
                'UploadId': upload_id,
                'PartNumber': part_number
            },
            ExpiresIn=3600
        )
        
        return {
            "url":url
        }
        
    def generate_all_presigned_urls(self,bucket_name:str,file_key:str,upload_id:str,total_parts:int):
        urls = []
        
        for part_number in range(1, total_parts + 1):
            url = self.generate_presigned_url(bucket_name, file_key, upload_id, part_number)['url']
            urls.append({
                "part_number": part_number,
                "url": url
            })
        return urls
        
    def complete_multipart_upload(self,bucket_name:str,file_key:str,upload_id:str,parts:list):
        
        res=self.s3.complete_multipart_upload(
            Bucket=bucket_name,
            Key=file_key,
            UploadId=upload_id,
            MultipartUpload={
                'Parts': parts
            }
        )
        
        return {
            "message": "Multipart upload completed successfully",
        }
        
    def download_object(self,bucket_name:str,file_key:str,download_path:str):
        
        self.s3.download_file(
            Bucket=bucket_name,
            Key=file_key,
            Filename=download_path
        )
        return {
            "message": "File downloaded successfully",
        }
        
    def upload_object(self,bucket_name:str,file_key:str,video_id:int):
        db=next(get_db())
        file_loc=file_key+".mp4"
        file_key_s3="videos/"+file_key
        self.s3.upload_file(
            Filename=file_loc,
            Bucket=bucket_name,
            Key=file_key_s3
        )
        update_video_status(db=db,video_id=video_id,status="uploaded")
        return {
            "message": "File uploaded successfully",
        }
        
s3=S3Config()
