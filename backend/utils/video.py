from sqlalchemy.orm import Session
from models.video import Video

def create_video(db:Session,file_key:str)->Video:
    new_video=Video(file_key=file_key)
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    print("Created video record with ID:", new_video.id)
    return new_video

def get_video(db:Session,video_id:int):
    return db.query(Video).filter(Video.id == video_id).first()

def update_video_status(db:Session,video_id:int,status:str):
    video=db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.status=status
        db.commit()
    return video