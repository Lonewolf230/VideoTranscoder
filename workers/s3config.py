import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError,BotoCoreError

load_dotenv()

class S3Config:

    def __init__(self):
        self.region_name=os.getenv("AWS_REGION")
        self.aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        self.bucket_name=os.getenv("BUCKET_NAME")
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def download_object(self,file_key, download_path):
        try:
            self.s3.download_file(
                Bucket=self.bucket_name,
                Key=file_key,
                Filename=download_path
            )
        except ClientError as e:
            raise Exception(str(e))
        
    def upload_object(self,file_key,video_id):
        try:
            file_loc=file_key+".mp4"
            file_key_s3="transcoded_videos/"+file_key
            self.s3.upload_file(
                Filename=file_loc,
                Bucket=self.bucket_name,
                Key=file_key_s3
            )
            return {
                "message": "File uploaded successfully",
            }
        except ClientError as e:
            raise Exception(str(e))
        

s3 = S3Config()