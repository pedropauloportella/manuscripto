import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings
from fastapi import UploadFile
import uuid

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY
        )

    def upload_file(self, file: UploadFile, folder: str = "manuscripts") -> str:
        file_extension = file.filename.split(".")[-1]
        file_key = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        try:
            self.s3.upload_fileobj(
                file.file,
                settings.MINIO_BUCKET,
                file_key
            )
            return file_key
        except Exception as e:
            raise Exception(f"Erro ao fazer upload para o S3: {str(e)}")

storage_service = StorageService()