from io import BytesIO
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from async_requests import get
from base.service import BaseService
from message.models.model import MessageModel
from message.schemas.schema import MessageSchema
from message.repositories.repository import MessageRepository
from attachment.services.service import AttachmentService
from attachment.models.model import AttachmentModel


class MessageService(BaseService[MessageModel]):
    '''
    Бизнес-логика сообщений
    '''

    def __init__(self, db: AsyncSession, attachment_service: AttachmentService):
        '''
        Бизнес-логика сообщений

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            MessageRepository(db),
            MessageModel,
            single_model_name="сообщение",
            multiple_models_name="сообщения"
        )
        self.attachment_service = attachment_service

    async def create(
        self,
        model: MessageModel,
        files_info: list[tuple[str, str]] | None = None
    ) -> MessageModel:
        '''
        Создать сообщение

        Args:
            model (MessageModel): SQL Alchemy модель сообщения
            files_info (list[tuple[str,str]]): Список `ID сообщения` и `URL медиа-контента`

        Returns:
            MessageModel: SQLAlchemy-модель сообщения

        Raises:
            WasNotCreatedError: Не удалось создать сообщение
        '''
        if not files_info:
            return await super().create(model)

        for f in files_info:
            attachment = await self.attachment_service.upload_files(f)
            if attachment:
                model.attachments.append(attachment)

        return await super().create(model)
