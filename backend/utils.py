import boto3
from botocore.exceptions import NoCredentialsError
from sqlalchemy.orm import Session
from models import Interview

# S3 클라이언트 초기화
s3 = boto3.client('s3', region_name='ap-northeast-2')

def upload_to_s3(file, bucket_name, object_name):
    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        s3_path = f"s3://{bucket_name}/{object_name}"
        return s3_path
    except NoCredentialsError:
        raise Exception("S3 Credentials not available")

def save_to_database(db: Session, s3_path: str, user_id: str, user_job: str, job_talent:str):
    interview = Interview(
        user_id=user_id,
        user_job=user_job,
        job_talent=job_talent,
        resume_path=s3_path
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview
