from configs.s3config import S3Config
from multiprocessing import Process
from configs.database import get_db
from utils.video import update_video_status
import os
from dotenv import load_dotenv
load_dotenv()

s3=S3Config()

def upload_files(input_path:list[str],video_id:int):
    
    processes=[]
    
    for path in input_path:
        print("Starting upload for file:", path)
        p=Process(target=upload_worker,args=(os.getenv("BUCKET_NAME"), path,video_id))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
def upload_worker(bucket_name:str,file_key:str,video_id:int):
    print(f"Uploading file {file_key} to bucket {bucket_name}...")
    s3.upload_object(
        bucket_name=bucket_name,
        file_key=file_key,
        video_id=video_id,
    )
    print(f"File {file_key} uploaded successfully.")
    
    
    