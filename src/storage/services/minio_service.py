from io import BytesIO
import os
import ssl
import uuid
import json
import asyncio
from minio import Minio
from minio.error import S3Error
from urllib3 import PoolManager, disable_warnings

from config import get_settings
from exceptions.exception import FileIsTooLargeError, WasNotCreatedError
from attachment.schemas.schema import AttachmentMinioSchema


class MinioService:
    def __init__(
        self,
        bucket_name: str,
        endpoint: str,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        context = ssl.create_default_context()
        context.options |= ssl.OP_NO_SSLv3 | ssl.OP_NO_SSLv2

        disable_warnings()

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
            http_client=PoolManager(
                cert_reqs="CERT_NONE"
            )
        )

        self._bucket_name = bucket_name

        __policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self._bucket_name}/*"]
                    }
                ]
            }
        )
        self.client.set_bucket_policy(self._bucket_name, __policy)
        self.__settings = get_settings()

    @classmethod
    def __split_file_name(cls, full_file_name: str) -> tuple[str, str]:
        '''
        Разделение полного имени файла на имя файла и его расширение

        Args:
            full_file_name (str): Полное имя файла с расширением

        Returns:
            tuple[str,str]: Первый объект - имя файла, \
                второй - расширение файла
        '''
        splitted = full_file_name.split(".")
        extension = splitted[-1]
        splitted.remove(extension)
        file_name = ".".join(splitted)
        return (file_name, extension)

    async def __ensure_bucket_exists(self):
        '''
        Проверка существования MinIO Bucket. В случае, если не существует, создает его

        Raises:
            S3Error: Ошибка MinIO
        '''
        try:
            exists = await asyncio.to_thread(
                self.client.bucket_exists,
                self.bucket_name
            )
            if not exists:
                await asyncio.to_thread(
                    self.client.make_bucket,
                    self.bucket_name
                )
        except S3Error as e:
            raise e

    async def upload_file(
        self,
        file: BytesIO,
        file_name: str,
        file_ext: str
    ) -> AttachmentMinioSchema:
        '''
        Загрузка файла в MinIO

        Args:
            file (BytesIO): Загружаемый файл
            file_name (str): Имя файла
            file_ext (str): Расширение файла

        Returns:
            AttachmentMinioSchema: Упрощенная Pydantic-схема медиа-контента, \
            прикрепляемого к теме с URL файла в MinIO

        Raises:
            FileIsTooLargeError: Размер файла превышает допустимый
            WasNotCreatedError: Не удалось загрузить файл в MinIO
            Exception: Прочие ошибки, связаныне с MinIO
        '''
        await self.__ensure_bucket_exists()

        try:
            full_file_name = f'{uuid.uuid4()}-{file_name}.{file_ext}'
            file_size = os.fstat(file.fileno()).st_size
            url = self.get_file_url(full_file_name)

            if file_size > self.__settings.attachment.max_size:
                raise FileIsTooLargeError(
                    "Максимальный размер файла - "
                    f"{self.__settings.attachment.max_size / 1024} Кбайт"
                )
            else:
                await asyncio.to_thread(
                    self.client.put_object,
                    self.bucket_name,
                    full_file_name,
                    file,
                    file_size,
                    # content_type=str(file.content_type)
                )

                return AttachmentMinioSchema(
                    minio_file_url='http://' + url,
                    file_name=str(file_name),
                    file_extension=file_ext,
                    file_size=file_size
                )
        except S3Error as exc:
            raise WasNotCreatedError(exc)

    @property
    def client(self) -> Minio:
        return self._client

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    def get_file_url(self, file_name: str) -> str:
        '''
        Получение URL файла в MinIO

        Args:
            file_name (str): Полное имя файла

        Returns:
            str: URL файла в MinIO
        '''
        return f"{self.__settings.minio.endpoint}/{self.bucket_name}/{file_name}"
