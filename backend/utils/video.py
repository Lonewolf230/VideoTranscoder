from sqlalchemy.orm import Session
from sqlalchemy import func
from models.video import Video
from exceptions import DatabaseError, VideoNotFoundError

def create_video(db: Session, file_key: str, file_name: str, file_size: int):
    try:
        video = Video(
            file_key=file_key,
            file_name=file_name,
            file_size=file_size
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    except Exception:
        db.rollback()
        raise DatabaseError("Failed to create video")


def delete_video_record(db: Session, video_id: int):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            db.delete(video)
            db.commit()
    except Exception:
        db.rollback()


def get_all_running_video_status(db: Session):
    try:
        videos = db.query(Video).filter(Video.status != "completed").all()
        return [
            {
                "id": v.id,
                "file_key": v.file_key,
                "status": v.status,
                "file_name": v.file_name
            }
            for v in videos
        ]
    except Exception:
        raise DatabaseError("Failed to fetch video statuses")


def get_total_storage_for_user(user_id: int, db: Session):
    try:
        total = db.query(Video).filter(Video.user_id == user_id)\
            .with_entities(func.sum(Video.file_size)).scalar()
        return total or 0
    except Exception:
        raise DatabaseError("Failed to calculate storage")