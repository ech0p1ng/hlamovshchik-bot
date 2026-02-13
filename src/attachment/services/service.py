from io import BytesIO
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from async_requests import download_file
from base.service import BaseService
from attachment.models.model import AttachmentModel
from attachment.schemas.schema import AttachmentSchema
from attachment.repositories.repository import AttachmentRepository
from exceptions.exception import FileIsTooLargeError, WasNotCreatedError, AlreadyExistsError
from storage.services.minio_service import MinioService


class AttachmentService(BaseService[AttachmentModel]):
    '''
    Бизнес-логика прикрепляемого медиа-контента
    '''

    def __init__(self, db: AsyncSession, minio_service: MinioService):
        '''
        Бизнес-логика прикрепляемого медиа-контента

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            AttachmentRepository(db),
            AttachmentModel,
            single_model_name="прикрепляемый медиа-контент",
            multiple_models_name="прикрепляемый медиа-контент"
        )
        self.minio_service = minio_service

    async def upload_files(
        self,
        *tg_msg_data: tuple[int, str]
    ) -> list[AttachmentModel] | None:
        '''
        Загрузка медиафайлов в MinIO и MinIO-ссылок на них в БД

        Args:
            tg_msg_data (tuple[int, str]): ID сообщения и URL медиа-контента

        Returns:
            list[AttachmentModel]|None: SQL-Alchemy созданного медиа-контента

        Raises:
            WasNotCreatedError: Не удалось загрузить в MinIO
            FileIsTooLargeError: Файл слишком большой для MinIO
            AlreadyExistsError: Данный медиафайл уже загружен
            Exception: Прочие ошибки MinIO
        '''
        models = []
        for message_id, file_url in tg_msg_data:
            response = await download_file(file_url)
            try:
                minio_schema = await self.minio_service.upload_file(
                    file=response['file'],
                    file_ext=response['ext']
                )
            except Exception as exc:
                raise Exception(f'MinIO: {exc}')
            else:
                model = AttachmentModel.from_schema(
                    minio_schema,
                    tg_msg_id=message_id,
                    tg_file_url=file_url,
                )

                filter = {
                    'tg_file_url': file_url
                }
                if await self.exists(filter, raise_exc=False):
                    raise AlreadyExistsError('Данный медиафайл уже загружен')
                model = await self.create(model)
                models.append(model)
        return models
