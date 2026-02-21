from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot_request.services.service import BotRequestService
from config import get_settings
from db.database import async_engine
from role.services.service import RoleService
from storage.services.minio_service import MinioService
from attachment.services.service import AttachmentService
from message.services.service import MessageService
from user.services.service import UserService
from botcommand.services.service import BotCommandService
from permission.services.service import PermissionService
from tg.bot.services.media import MediaService
from global_var.services.service import GlobalVarService

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


async def get_global_var_service(db: AsyncSession) -> GlobalVarService:
    return GlobalVarService(db)


async def get_message_service(db: AsyncSession) -> MessageService:
    return MessageService(
        db,
        await get_attachment_service(db),
        await get_global_var_service(db),
    )


async def get_role_service(db: AsyncSession) -> RoleService:
    return RoleService(db)


async def get_botcommand_service(db: AsyncSession) -> BotCommandService:
    return BotCommandService(db)


async def get_permission_service(db: AsyncSession) -> PermissionService:
    return PermissionService(
        db,
        await get_botcommand_service(db),
        await get_role_service(db)
    )


async def get_user_service(db: AsyncSession) -> UserService:
    return UserService(db, await get_permission_service(db))


async def get_media_service(db: AsyncSession) -> MediaService:
    return MediaService(
        db,
        await get_message_service(db),
        get_minio_service(),
    )


async def get_bot_request_service(db: AsyncSession) -> BotRequestService:
    return BotRequestService(db)