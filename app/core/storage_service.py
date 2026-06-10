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
    
    def upload_file(self, file, filename: str) -> str:
        self.client.upload_fileobj(file, "resumes", filename)
        return filename
    
    def get_file_url(self, filename: str) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "resumes", "Key": filename},
            ExpiresIn=900  
        )