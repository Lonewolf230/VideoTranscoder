from models.video import Video
from sqlalchemy.orm import Session
from utils.video import get_video_data,delete_videos_from_s3,delete_video_record,update_video_status,get_presigned_download_urls_s3
from exceptions import UnAuthorizedError


def delete_video(video_id:int,db:Session,user_id:int):
    
    video : Video = get_video_data(db=db,video_id=video_id)
    
    if video.user_id != user_id:
        raise UnAuthorizedError("Unauthorized to delete this video")

    if video:
        print("Video",video.file_key)
        update_video_status(db=db, video_id=video_id, status="deleting")
        delete_videos_from_s3(video.file_key)
        delete_video_record(db=db, video_id=video_id)
        
def get_presigned_download_urls(video_id:int, db:Session,user_id:int):

    return get_presigned_download_urls_s3(video_id=video_id, db=db,user_id=user_id)
        
    