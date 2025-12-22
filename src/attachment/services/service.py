from io import BytesIO
from minio import S3Error
from sqlalchemy.ext.asyncio import AsyncSession

from async_requests import get
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
        *tg_msg_data: tuple[str, str]
    ) -> None:
        '''
        Загрузка медиафайлов в MinIO и MinIO-ссылок на них в БД

        Raises:
            WasNotCreatedError: Не удалось загрузить в MinIO
            FileIsTooLargeError: Файл слишком большой для MinIO
            Exception: Прочие ошибки MinIO
        '''
        for message_id, file_url in tg_msg_data:
            response = await self.__download_file(file_url)
            try:
                minio_schema = await self.minio_service.upload_file(*response)
            except S3Error as exc:
                raise WasNotCreatedError(f"MinIO: {exc}")
            except FileIsTooLargeError as exc:
                raise FileIsTooLargeError(f"MinIO: {exc}")
            except Exception as exc:
                raise Exception(f'MinIO: {exc}')

            # TODO Проверить работу в MinIO через докер
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
            await self.create(model)

    async def __download_file(self, url: str) -> tuple[BytesIO, str, str]:
        '''
        Скачать файл из `url`

        Args:
            url (str): URL медиа-файла

        Returns:
            tuple[BytesIO,str,str]: Загруженный файл, его имя и расширение

        Raises:
            httpx.HTTPError: Не удалось загрузить `url`: `status_code`
        '''
        full_file_name = url.split('/')[-1]
        file_ext = full_file_name.split('.')[-1]
        file_name = full_file_name.replace(f'.{file_ext}', '')
        response = await get(url)
        file = BytesIO(response.content)
        return file, file_name, file_ext
