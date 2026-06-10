import boto3
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_URL,
            aws_access_key_id=settings.MINIO_USER,
            aws_secret_access_key=settings.MINIO_PASSWORD
        )
        self.public_client = boto3.client(
            "s3",
            endpoint_url=settings.MINIO_PUBLIC_URL,
            aws_access_key_id=settings.MINIO_USER,
            aws_secret_access_key=settings.MINIO_PASSWORD
        )
    
    def get_file_url(self, filename: str) -> str:
        return self.public_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "resumes", "Key": filename},
            ExpiresIn=900
        )