from sqlalchemy.orm import Mapped, mapped_column
from base.model import BaseModel
from attachment.schemas.schema import (
    AttachmentSchema, AttachmentSimpleSchema, AttachmentMinioSchema
)


class AttachmentModel(BaseModel):
    '''
    SQL Alchemy модель медиа файла

    Args:
        id (int): Идентификатор
        tg_msg_id (Mapped[str]): Идентификатор сообщения
        tg_file_url (Mapped[str]): URL файла на серверах telegram
        minio_file_url (Mapped[str]): Адрес хранения файла
        file_name (Mapped[str]): Имя файла
        file_extension (Mapped[str]): Расширение файла
        file_size (Mapped[int]): Размер файла в байтах
        block (BlockModel): Блок, к которому относится прикрепленный файл
    '''
    __tablename__ = 'attachment'

    tg_msg_id: Mapped[str] = mapped_column(nullable=False)
    tg_file_url: Mapped[str] = mapped_column(nullable=False)
    minio_file_url: Mapped[str] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column()
    file_extension: Mapped[str] = mapped_column()
    file_size: Mapped[int] = mapped_column()

    def __eq__(self, value: object) -> bool:

        if isinstance(value, AttachmentModel):
            self_stats = (
                self.file_name,
                self.file_extension,
                self.file_size
            )
            value_stats = (
                value.file_name,
                value.file_extension,
                value.file_size
            )
            return self_stats == value_stats
        else:
            return False

    @classmethod
    def from_schema(
        cls,
        schema: AttachmentSimpleSchema |
            AttachmentSchema | AttachmentMinioSchema
    ) -> 'AttachmentModel':
        if type(schema) is AttachmentSchema:
            return cls(
                minio_file_url=schema.minio_file_url,
                file_name=schema.file_name,
                file_extension=schema.file_extension,
                file_size=schema.file_size,
                block_id=schema.block_id
            )
        elif type(schema) is AttachmentMinioSchema:
            return cls(
                minio_file_url=schema.minio_file_url,
                file_name=schema.file_name,
                file_extension=schema.file_extension,
                file_size=schema.file_size
            )
        else:
            return cls(
                file_name=schema.file_name,
                file_extension=schema.file_extension,
                file_size=schema.file_size
            )
