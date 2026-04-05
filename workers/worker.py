from workers.sqs import sqs_client as sqs
from workers.s3config import s3
from workers.transcoder import transcode_video
from workers.upload_files import upload_files
from workers.video import update_video_status,get_video_status
from workers.database import SessionLocal
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time


def worker():
    while True:
        flag=True
        db=None
        video_id=None
        success=False
        receipt_handle=None
        download_path=None
        try:
            db=SessionLocal()
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
            
            vid_status=get_video_status(db=db, video_id=video_id)
            if vid_status == "deleting":
                print(f"Video ID: {video_id} is marked for deletion, skipping processing.")
                continue


            print(f"Processing video ID: {video_id} with file key: {file_key}")
            
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
            
            if not os.path.exists(download_path + ".mp4"):
                s3.download_object(
                    bucket_name=os.getenv("BUCKET_NAME"),
                    file_key=file_key,
                    download_path=download_path + ".mp4"  
                )
            
            else:
                print(f"File {download_path + '.mp4'} already exists locally, skipping download.")

            update_video_status(db=db, video_id=video_id, status="transcoding")
            
            transcode_video(input_path=download_path + ".mp4")

            update_video_status(db=db, video_id=video_id, status="uploading_back")
            
            upload_files(
                input_path=[f"{download_path}_480p", f"{download_path}_720p"],
                video_id=video_id
            )    
            
            update_video_status(db=db, video_id=video_id, status="completed")
            success=True
        except Exception as e:
            print(f"Error occurred: {e}")
            if video_id and db:
                update_video_status(db=db, video_id=video_id, status="failed")    
                
        finally:
            if success and receipt_handle:
                print("Processing complete, deleting message and local files...")
                try:
                    print("Deleting message from queue...")
                    sqs.delete_message(receipt_handle)
                    
                except Exception as e:
                    print(e)
            # flag=False
            
            #cleanup
            if success and download_path:
                for suffix in ["_480p.mp4", "_720p.mp4", ".mp4"]:
                    path = download_path + suffix
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                            print(f"Deleted local file: {path}")
                    except Exception as e:
                        print(f"Error deleting file {path}: {e}")
                        
            elif not success and download_path:
                for suffix in ["_480p.mp4", "_720p.mp4"]:
                    path = download_path + suffix
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                            print(f"Deleted local file: {path}")
                    except Exception as e:
                        print(f"Error deleting file {path}: {e}")
            
            
            if db:
                db.close()
                
            
if __name__ == "__main__":
    worker()