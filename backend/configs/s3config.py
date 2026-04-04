import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError,BotoCoreError
from exceptions import S3UploadError
import uuid

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
            print(f"Error completing multipart upload for {file_key}: {e}")
            raise S3UploadError(str(e))

    def delete_object(self, bucket_name, file_key):
        try:
            print(f"Deleting object {file_key} from bucket {bucket_name}")
            self.s3.delete_object(Bucket=bucket_name, Key=file_key)
        except (ClientError, BotoCoreError) as e:
            raise 
        
    def delete_objects(self,bucket_name,file_keys:list):

        keys=[{"Key": key} for key in file_keys]
        try:
            self.s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": keys
                }
            )
        except (ClientError, BotoCoreError) as e:
            raise

    def download_object(self, bucket_name, file_key, download_path):
        try:
            self.s3.download_file(
                Bucket=bucket_name,
                Key=file_key,
                Filename=download_path
            )
        except ClientError as e:
            raise S3UploadError(str(e))
        
    def upload_object(self, bucket_name, file_key,video_id):
        try:
            file_loc=file_key+".mp4"
            file_key_s3="transcoded_videos/"+file_key
            self.s3.upload_file(
                Filename=file_loc,
                Bucket=bucket_name,
                Key=file_key_s3
            )
            return {
                "message": "File uploaded successfully",
            }
        except ClientError as e:
            raise S3UploadError(str(e))
        
        
    def generate_download_presigned_url(self,bucket_name:str,file_key:str,expires_in:int=3600):
        try:
            url=self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_key,
                    'ResponseContentDisposition':f'attachment; filename="{uuid.uuid4()}.mp4"'
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise S3UploadError(str(e))
        
    def get_all_download_presigned_urls(self,bucket_name:str,file_key:str,expires_in:int=3600) -> list:
        try:
            urls=[]
            original_url=self.generate_download_presigned_url(bucket_name,file_key,expires_in)
            urls.append(original_url)
            for res in ["720p", "480p"]:
                key=file_key.replace("videos/", "transcoded_videos/")+f"_{res}"
                url=self.generate_download_presigned_url(bucket_name,key,expires_in)
                urls.append(url)
            return urls
        except (ClientError, BotoCoreError) as e:
            raise 


s3 = S3Config()