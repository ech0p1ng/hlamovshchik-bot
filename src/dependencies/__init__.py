from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from config import get_settings
from db.database import async_engine, get_db
from storage.services.minio_service import MinioService
from attachment.services.service import AttachmentService
from message.services.service import MessageService

SessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)


def get_minio_service():
    minio_settings = get_settings().minio
    return MinioService(
        minio_settings.bucket_name,
        minio_settings.endpoint,
        minio_settings.access_key,
        minio_settings.secret_key
    )


async def get_attachment_service(db: AsyncSession) -> AttachmentService:
    return AttachmentService(db, get_minio_service())


async def get_message_service(db: AsyncSession) -> MessageService:
    attachment_service = await get_attachment_service(db)
    return MessageService(db, attachment_service)
