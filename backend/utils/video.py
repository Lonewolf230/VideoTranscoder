from sqlalchemy.orm import Session
from models.video import Video

def create_video(db:Session,file_key:str,file_name:str)->Video:
    try:
        new_video=Video(file_key=file_key,file_name=file_name)
        db.add(new_video)
        db.commit()
        db.refresh(new_video)
        print("Created video record with ID:", new_video.id)
        return new_video

    except Exception as e:
        db.rollback()
        print("Error creating video record:", e)
        raise 

def get_video_status(db:Session,video_id:int):
    try:
        video=db.query(Video).filter(Video.id == video_id).first()
        if video:
            print(f"Video ID {video_id} status: {video.status}")
            return video.status
        else:
            print(f"Video ID {video_id} not found")
            return None
    except Exception as e:
        print("Error fetching video status:", e)
        raise 

def update_video_status(db:Session,video_id:int,status:str):
    try:
        video=db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status=status
            db.commit()
            print(f"Updated video ID {video_id} status to: {status}")
        else:
            print(f"Video ID {video_id} not found for status update")
    except Exception as e:
        db.rollback()
        print("Error updating video status:", e)
        raise 
    
def get_all_running_video_status(db:Session):
    try:
        videos=db.query(Video).filter(Video.status != "completed").all()
        return [{"id":v.id,"file_key":v.file_key,"status":v.status,"file_name":v.file_name} for v in videos]
    except Exception as e:
        print("Error fetching all video statuses:", e)
        raise
    
def get_finished_videos(db:Session):
    try:
        videos=db.query(Video).filter(Video.status == "completed").all()
        return [{"id":v.id,"file_key":v.file_key,"status":v.status,"file_name":v.file_name} for v in videos]
    except Exception as e:
        print("Error fetching finished videos:", e)
        raise
