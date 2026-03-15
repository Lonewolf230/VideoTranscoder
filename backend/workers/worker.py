from configs.sqs import sqs_client as sqs
from configs.s3config import s3
from .transcoder import transcode_video
from .upload_files import upload_files
from utils.video import update_video_status
from configs.database import get_db
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time

flag=True

db=next(get_db())

while flag:

    try:
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
        
        
        
        download_path = file_key.split('/')[1]
        print(f"Download path : {download_path}")
        # Strip .mp4 extension if already present in the S3 key
        if download_path.endswith('.mp4'):
            download_path = download_path[:-4]

        print(f"Download path set to: {download_path}")

        file_key = "videos/" + download_path  # reconstruct clean S3 key
        print(f"Full file key for S3 operations: {file_key}")
        print(download_path)
        
        update_video_status(db=db, video_id=video_id, status="processing")
        
        s3.download_object(
            bucket_name=os.getenv("BUCKET_NAME"),
            file_key=file_key,
            download_path=download_path + ".mp4"  
        )

        update_video_status(db=db, video_id=video_id, status="transcoding")
        
        transcode_video(input_path=download_path + ".mp4")

        update_video_status(db=db, video_id=video_id, status="uploading_back")
        
        upload_files(
            input_path=[f"{download_path}_480p", f"{download_path}_720p"],
            video_id=video_id
        )    
        
        update_video_status(db=db, video_id=video_id, status="completed")
        sqs.delete_message(receipt_handle=receipt_handle)
        flag=False
        
        
    except Exception as e:
        print(f"Error occurred: {e}")
        update_video_status(db=db, video_id=video_id, status="failed")
    