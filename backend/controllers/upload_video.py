import os
import json
import uuid
from dotenv import load_dotenv

from configs.s3config import s3
from configs.sqs import sqs_client as sqs
from utils.video import create_video, delete_video_record
from exceptions import S3UploadError, DatabaseError, SQSMessageError

load_dotenv()

BUCKET = os.getenv("BUCKET_NAME")


def generate_multipart_upload(file_name: str):
    file_key = f"videos/{uuid.uuid4()}"

    return s3.create_multipart_upload(
        bucket_name=BUCKET,
        file_key=file_key,
        file_name=file_name
    )


def generate_all_presigned_urls(upload_id: str, total_parts: int, file_key: str):
    return s3.generate_all_presigned_urls(
        bucket_name=BUCKET,
        file_key=file_key,
        upload_id=upload_id,
        total_parts=total_parts
    )


def complete_multipart_upload(upload_id, parts, file_key, db, file_name, file_size):

    # STEP 1: complete upload
    s3.complete_multipart_upload(
            bucket_name=BUCKET,
            file_key=file_key,
            upload_id=upload_id,
            parts=parts
        )


    # STEP 2: DB entry
    try:
        video = create_video(db, file_key, file_name, file_size)
    except DatabaseError:
        s3.delete_object(BUCKET, file_key)
        raise

    # STEP 3: send message
    message = {
        "file_key": video.file_key,
        "video_id": video.id
    }

    try:
        sqs.send_message(json.dumps(message))
    except SQSMessageError:
        delete_video_record(db, video.id)
        s3.delete_object(BUCKET, file_key)
        raise

    return message