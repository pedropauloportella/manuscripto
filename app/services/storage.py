import boto3
from botocore.config import Config
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4')
        )

    def upload_file(self, file) -> str:
        """Realiza upload para o bucket do Supabase."""
        file_key = f"manuscripts/{file.filename}"
        self.s3.upload_fileobj(file.file, settings.S3_BUCKET, file_key)
        return file_key

    def get_presigned_url(self, file_key: str, expires_in: int = 3600) -> str:
        """Gera uma URL temporária para download seguro."""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.S3_BUCKET, 'Key': file_key},
            ExpiresIn=expires_in
        )

storage_service = StorageService()