import boto3
from fastapi import UploadFile
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        self.bucket = settings.S3_BUCKET

    def upload_file(self, file: UploadFile) -> str:
        # Gera um caminho único para evitar sobrescrita
        file_key = f"manuscripts/{file.filename}"
        self.s3.upload_fileobj(
            file.file,
            self.bucket,
            file_key,
            ExtraArgs={"ContentType": file.content_type}
        )
        return file_key

    def get_presigned_url(self, file_key: str, expires_in: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": file_key},
            ExpiresIn=expires_in,
        )

storage_service = StorageService()