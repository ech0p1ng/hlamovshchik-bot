from io import BytesIO
from typing import Any
from uuid import uuid4
from minio import S3Error
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from attachment.models.model import AttachmentModel
from attachment.repositories.repository import AttachmentRepository
from exceptions.exception import FileIsTooLargeError, WasNotCreatedError

from base.service import BaseService
from storage.services.minio_service import MinioService
from config import settings
from exceptions.exception import NotFoundError
from async_requests import get


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
        *file_urls: str
    ) -> None:
        for file_url in file_urls:
            response = await self.__download_file(file_url)
            try:
                schema = await self.minio_service.upload_file(*response)
            except S3Error as exc:
                raise WasNotCreatedError(f"MinIO: {exc}")
            except FileIsTooLargeError as exc:
                raise FileIsTooLargeError(f"MinIO: {exc}")
            except Exception as exc:
                raise Exception(f'MinIO: {exc}')

            model = AttachmentModel.from_schema(schema)
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
