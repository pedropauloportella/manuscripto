import boto3
from app.core.config import settings

def init_bucket():
    """
    Inicializa o bucket no MinIO caso ele não exista.
    """
    s3 = boto3.client(
        's3',
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY
    )
    
    try:
        s3.create_bucket(Bucket=settings.MINIO_BUCKET)
        print(f"Bucket '{settings.MINIO_BUCKET}' criado com sucesso.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{settings.MINIO_BUCKET}' já existe.")

if __name__ == "__main__":
    init_bucket()