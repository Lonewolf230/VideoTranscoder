from sqlalchemy.orm import Session
from sqlalchemy import func
from models.video import Video
from models.user import User
from exceptions import DatabaseError, VideoNotFoundError,UnAuthorizedError
from configs.s3config import s3
import os
from dotenv import load_dotenv
load_dotenv()

def create_video(db: Session, file_key: str, file_name: str, file_size: int,user_id:int):
    try:
        video = Video(
            user_id=user_id,
            file_key=file_key,
            file_name=file_name,
            file_size=file_size
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return video

    except Exception as e:
        db.rollback()
        print(f"Error creating video record for {file_key}: {e}")
        raise DatabaseError("Failed to create video") from e
    
def update_video_status(db:Session, video_id:int, status:str):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} not found")
        video.status = status
        db.commit()
    except VideoNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError("Failed to update video status") from e


def delete_video_record(db: Session, video_id: int):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            db.delete(video)
            db.commit()
    except Exception as e:
        db.rollback()
        raise DatabaseError("Failed to delete video record") from e


def get_all_running_video_status(db: Session):
    try:
        videos = db.query(Video).all()
        return [
            {
                "id": v.id,
                "file_key": v.file_key,
                "status": v.status,
                "file_name": v.file_name,
                "file_size": v.file_size
            }
            for v in videos
        ]
    except Exception:
        raise DatabaseError("Failed to fetch video statuses")


def get_total_storage_for_user(user_id: int, db: Session):
    try:
        total = db.query(Video).filter(Video.user_id == user_id).with_entities(func.sum(Video.file_size)).scalar()
        print(total)
        return total or 0
    except Exception as e:
        raise DatabaseError("Failed to calculate storage") from e
    
def get_video_status(db: Session, video_id: int):
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} not found")
        return video.status
    except VideoNotFoundError:
        raise
    except Exception as e:
        raise DatabaseError("Failed to fetch video status") from e
    
def get_video_data(db:Session,video_id:int):
    try:
        video=db.query(Video).filter(Video.id==video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} not found")
        return video
    except VideoNotFoundError:
        raise
    except Exception as e:
        raise DatabaseError("Failed to fetch video data") from e
    
def delete_videos_from_s3(file_key:str):
    print(f"Deleting video with file key {file_key} from S3")
    transcoded_keys= [file_key.replace("videos/","transcoded_videos/")+f"_{res}" for res in ["720p", "480p"]]
    file_keys=[file_key] + transcoded_keys
    s3.delete_objects(file_keys=file_keys)

def get_presigned_download_urls_s3(video_id:int, db:Session,user_id:int)-> list:
    video : Video = get_video_data(db=db,video_id=video_id)
    
    if not video:
        raise VideoNotFoundError(f"Video with id {video_id} not found")
    
    if video.user_id != user_id:
        raise UnAuthorizedError("Unauthorized to access this video")
    
    urls = s3.get_all_download_presigned_urls(
            file_key=video.file_key,
            expires_in=3600
        )
    return urls

                    