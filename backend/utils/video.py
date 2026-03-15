from sqlalchemy.orm import Session
from models.video import Video

def create_video(db:Session,file_key:str)->Video:
    new_video=Video(file_key=file_key)
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    print("Created video record with ID:", new_video.id)
    return new_video

def get_video_status(db:Session,video_id:int):
    video=db.query(Video).filter(Video.id == video_id).first()
    return video.status if video else None

def update_video_status(db:Session,video_id:int,status:str):
    video=db.query(Video).filter(Video.id == video_id).first()
    print(f"Updating video ID {video_id} status to {status}")
    if video:
        video.status=status
        db.commit()
    return video