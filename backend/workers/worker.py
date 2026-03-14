from configs.sqs import sqs_client as sqs
from configs.s3config import s3
from .transcoder import transcode_video
from .upload_files import upload_files
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time

flag=True
while flag:
    print("Checking for messages in the queue...")
    print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')} before receive")
    message=sqs.receive_message()
    print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')} after receive")
    
    if not message:
        print("No messages in the queue, waiting...")
        continue
    
    print(f"Received message: {message}")
    message_body=json.loads(message[0]['Body'])
    receipt_handle=message[0]['ReceiptHandle']
    file_key=message_body['file_key']
    video_id=message_body['video_id']
    
    # print(f"Processing video with file key: {file_key} and video ID: {video_id}")
    # download_path=file_key.split('/')[1]
    # print(f"Download path set to: {download_path}")
    # # downloaded_path=download_path+".mp4"
    # # print(downloaded_path)
    # # print(download_path+"_480p.mp4")
    # file_key="videos/"+download_path
    # print(f"Full file key for S3 operations: {file_key}")
    # #download file locally
    # s3.download_object(
    #     bucket_name=os.getenv("BUCKET_NAME"),
    #     file_key=file_key,
    #     download_path=download_path+".mp4"
    # )
    # print("Video downloaded successfully, starting transcoding...")
    # transcode_video(input_path=download_path+".mp4")
    # print("Transcoding completed, uploading transcoded video...")
    
    # upload_files(input_path=[f"{download_path}_480p",f"{download_path}_720p"],video_id=video_id)
    
    download_path = file_key.split('/')[1]
    print(f"Download path : {download_path}")
    # Strip .mp4 extension if already present in the S3 key
    if download_path.endswith('.mp4'):
        download_path = download_path[:-4]

    print(f"Download path set to: {download_path}")

    file_key = "videos/" + download_path  # reconstruct clean S3 key
    print(f"Full file key for S3 operations: {file_key}")
    print(download_path)
    s3.download_object(
        bucket_name=os.getenv("BUCKET_NAME"),
        file_key=file_key,
        download_path=download_path + ".mp4"  
    )

    transcode_video(input_path=download_path + ".mp4")

    upload_files(
        input_path=[f"{download_path}_480p", f"{download_path}_720p"],
        video_id=video_id
    )    
    sqs.delete_message(receipt_handle=receipt_handle)
    flag=False
    
    
    
    
    
    
    