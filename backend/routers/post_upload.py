from fastapi import APIRouter, Depends, HTTPException
from controllers.post_upload import delete_video as delete_vid_controller,get_presigned_download_urls as get_presigned_download_urls_controller
from configs.database import get_db
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from exceptions import DatabaseError,VideoNotFoundError,UnAuthorizedError
from botocore.exceptions import ClientError,BotoCoreError

post_upload_router = APIRouter()


@post_upload_router.delete("/delete-video/{video_id}")
def delete_video(video_id: int,db=Depends(get_db),user_id=Depends(get_current_user)):
    # Implement logic to delete video from S3 and database
    try:
        delete_vid_controller(video_id=video_id, db=db,user_id=user_id)
        return {"message": f"Video with ID {video_id} deleted successfully"}
    
    except VideoNotFoundError as e:
        raise HTTPException(status_code=200,detail="Video already deleted or not found")
    
    except UnAuthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"S3 error: {str(e)}")
    
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@post_upload_router.get("/presigned-download-urls/{video_id}")
def get_presigned_download_urls(video_id: int, db=Depends(get_db),user_id=Depends(get_current_user)):

    try:
        urls=get_presigned_download_urls_controller(video_id=video_id, db=db,user_id=user_id)
        return urls
    except VideoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnAuthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (ClientError, BotoCoreError) as e:
        raise HTTPException(status_code=502, detail=f"S3 error: {str(e)}")
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))