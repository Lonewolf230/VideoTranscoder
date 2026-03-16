from configs.s3config import S3Config
from multiprocessing import Process,set_start_method
from configs.database import get_db
from utils.video import update_video_status
import os
from dotenv import load_dotenv
load_dotenv()

s3=S3Config()

def upload_files(input_path:list[str],video_id:int):
    ctx=__import__("multiprocessing").get_context("spawn")
    processes=[]
    
    for path in input_path:
        print("Starting upload for file:", path)
        p=ctx.Process(target=upload_worker,args=(os.getenv("BUCKET_NAME"), path,video_id))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
    
    failed=[i for i,p in enumerate(processes) if p.exitcode !=0]
    if failed:
        raise RuntimeError(f"Upload failed for paths: {[input_path[i] for i in failed]}")

        
def upload_worker(bucket_name:str,file_key:str,video_id:int):
    db=None
    try:
        db=next(get_db())

        s3.upload_object(bucket_name=bucket_name,file_key=file_key,video_id=video_id)
        print(f"Upload complete for file: {file_key}")
    except Exception as e:
        print(f"Error uploading file {file_key}:", e)
        if db:
            update_video_status(db=next(get_db()), video_id=video_id, status="failed")
        raise
    finally:
        if db:
            db.close()
    
    
    