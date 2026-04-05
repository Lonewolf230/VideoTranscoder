
from workers.models.video import Video
from workers.models.user import User
from sqlalchemy.orm import Session

def update_video_status(db:Session, video_id:int, status:str):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise Exception(f"Video with id {video_id} not found")
        video.status = status
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception("Failed to update video status") from e
    
def get_video_status(db: Session, video_id: int):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise Exception(f"Video with id {video_id} not found")
        return video.status
    except Exception as e:
        raise Exception("Failed to fetch video status") from e