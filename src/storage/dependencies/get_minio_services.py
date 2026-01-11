from config import get_settings
from storage.services.minio_service import MinioService

minio_client = MinioService


def get_minio_service() -> MinioService:
    return MinioService(
        get_settings().minio.bucket_name,
        get_settings().minio.endpoint,
        get_settings().minio.access_key,
        get_settings().minio.secret_key,
    )
