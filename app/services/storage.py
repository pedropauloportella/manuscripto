import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings
from fastapi import UploadFile
import uuid

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )

    def upload_file(self, file: UploadFile, folder: str = "manuscripts") -> str:
        file_extension = file.filename.split(".")[-1]
        file_key = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        try:
            self.s3.upload_fileobj(
                file.file,
                settings.S3_BUCKET,
                file_key
            )
            return file_key
        except Exception as e:
            raise Exception(f"Erro ao fazer upload para o S3: {str(e)}")

    def get_presigned_url(self, file_key: str, expires_in: int = 3600) -> str:
        """
        Gera uma URL temporária para acesso ao arquivo no S3/MinIO.
        """
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.S3_BUCKET, 'Key': file_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            raise Exception(f"Erro ao gerar URL assinada: {str(e)}")

storage_service = StorageService()