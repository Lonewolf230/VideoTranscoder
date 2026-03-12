import boto3


class S3Config:

    def __init__(self, access_key: str, secret_key: str, region: str):
        self.s3=boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
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
        