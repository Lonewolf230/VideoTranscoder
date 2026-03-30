# import boto3
# import os
# from dotenv import load_dotenv
# from sqlalchemy.orm import Session
# from configs.database import get_db
# from utils.video import update_video_status
# from botocore.exceptions import ClientError,BotoCoreError
# from fastapi import HTTPException
# load_dotenv()

# class S3Config:

#     def __init__(self):
#         self.s3=boto3.client(
#             's3',
#             aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#             aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#             region_name=os.getenv("AWS_REGION")
#         )

        
#     def create_multipart_upload(self, bucket_name: str, file_key: str,file_name:str):
        
#         try:
#             response = self.s3.create_multipart_upload(
#                 Bucket=bucket_name,
#                 Key=file_key,
#                 ContentType='video/mp4',
#                 Metadata={
#                     'file_name': file_name
#                 }
#             )

#             return {
#                 "upload_id": response['UploadId'],
#                 "file_key": file_key
#             }
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")
    
#     def generate_presigned_url(self, bucket_name: str, file_key: str, upload_id: str, part_number: int):
        
#         try:
#             url = self.s3.generate_presigned_url(
#                 ClientMethod='upload_part',
#                 Params={
#                     'Bucket': bucket_name,
#                     'Key': file_key,
#                     'UploadId': upload_id,
#                     'PartNumber': part_number
#                 },
#                 ExpiresIn=3600
#             )
            
#             return {
#                 "url":url
#             } 
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")
        
#     def generate_all_presigned_urls(self,bucket_name:str,file_key:str,upload_id:str,total_parts:int):
#         urls = []
        
#         try:
#             for part_number in range(1, total_parts + 1):
#                 url = self.generate_presigned_url(bucket_name, file_key, upload_id, part_number)['url']
#                 urls.append({
#                     "part_number": part_number,
#                     "url": url
#                 })
#             return urls
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")
        
#     def complete_multipart_upload(self,bucket_name:str,file_key:str,upload_id:str,parts:list):
        
#         try:
#             self.s3.complete_multipart_upload(
#                 Bucket=bucket_name,
#                 Key=file_key,
#                 UploadId=upload_id,
#                 MultipartUpload={
#                     'Parts': parts
#                 }
#             )
            
#             return {
#                 "message": "Multipart upload completed successfully",
#             }
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")

#     def delete_object(self, bucket_name: str, file_key: str):
#         try:
#             self.s3.delete_object(Bucket=bucket_name, Key=file_key)
#         except ClientError as e:
#             print(f"WARNING: S3 cleanup failed for key {file_key}: {e}")
        
#     def download_object(self,bucket_name:str,file_key:str,download_path:str):
        
#         try:
#             self.s3.download_file(
#                 Bucket=bucket_name,
#                 Key=file_key,
#                 Filename=download_path
#             )
#             return {
#                 "message": "File downloaded successfully",
#             }
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")
        
#     def upload_object(self,bucket_name:str,file_key:str,video_id:int):
#         try:
#             file_loc=file_key+".mp4"
#             file_key_s3="transcoded_videos/"+file_key
#             self.s3.upload_file(
#                 Filename=file_loc,
#                 Bucket=bucket_name,
#                 Key=file_key_s3
#             )
#             return {
#                 "message": "File uploaded successfully",
#             }
#         except ClientError as e:
#             code = e.response['Error']['Code']
#             raise HTTPException(status_code=502, detail=f"S3 error [{code}]: {e}")
        
            
# s3=S3Config()

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from exceptions import S3UploadError

load_dotenv()

class S3Config:

    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

    def create_multipart_upload(self, bucket_name, file_key, file_name):
        try:
            response = self.s3.create_multipart_upload(
                Bucket=bucket_name,
                Key=file_key,
                ContentType='video/mp4',
                Metadata={'file_name': file_name}
            )

            return {
                "upload_id": response['UploadId'],
                "file_key": file_key
            }

        except ClientError as e:
            raise S3UploadError(str(e))

    def generate_presigned_url(self, bucket_name, file_key, upload_id, part_number):
        try:
            return self.s3.generate_presigned_url(
                ClientMethod='upload_part',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_key,
                    'UploadId': upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=3600
            )
        except ClientError as e:
            raise S3UploadError(str(e))

    def generate_all_presigned_urls(self, bucket_name, file_key, upload_id, total_parts):
        try:
            urls = []
            for part_number in range(1, total_parts + 1):
                url = self.generate_presigned_url(bucket_name, file_key, upload_id, part_number)
                urls.append({
                    "part_number": part_number,
                    "url": url
                })
            return urls
        except Exception as e:
            raise S3UploadError(str(e))

    def complete_multipart_upload(self, bucket_name, file_key, upload_id, parts):
        try:
            self.s3.complete_multipart_upload(
                Bucket=bucket_name,
                Key=file_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
        except ClientError as e:
            raise S3UploadError(str(e))

    def delete_object(self, bucket_name, file_key):
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=file_key)
        except ClientError:
            # cleanup failure should NOT crash system
            pass


s3 = S3Config()