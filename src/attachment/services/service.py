from minio import S3Error
from base.service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from attachment.models.model import AttachmentModel
from attachment.repositories.repository import AttachmentRepository
from exceptions.exception import FileIsTooLargeError, WasNotCreatedError
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

    # TODO: Изменить тайпхинт для files
    async def upload_files(
        self,
        *files: UploadFile
    ) -> list[AttachmentModel]:
        uploaded_attachments = []
        for file in files:
            try:
                attachment_schema = await self.minio_service.upload_file(file)
            except S3Error as exc:
                raise WasNotCreatedError(f"MinIO: {exc}")
            except FileIsTooLargeError as exc:
                raise FileIsTooLargeError(f"MinIO: {exc}")
            except Exception as exc:
                raise Exception(f'MinIO: {exc}')

            attachment_model = AttachmentModel.from_schema(
                attachment_schema)
            uploaded_attachments.append(attachment_model)
        return uploaded_attachments
