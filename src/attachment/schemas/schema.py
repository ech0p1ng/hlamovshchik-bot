from pydantic import Field
from base.schema import BaseSchema, BaseSimpleSchema


class AttachmentSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема медиа-контента, прикрепляемого к теме

    Args:
        file_name (str): Имя файла
        file_extension (str): Расширение файла
        file_size (int): Размер файла (байт)
    '''
    file_name: str
    file_extension: str
    file_size: int


class AttachmentMinioSchema(AttachmentSimpleSchema):
    '''
    Упрощенная Pydantic-схема медиа-контента, \
        прикрепляемого к теме с URL файла в MinIO

    Args:
        minio_file_url (str | None): Ссылка на файл в MinIO
        file_name (str): Имя файла
        file_extension (str): Расширение файла
        file_size (int): Размер файла (байт)
    '''

    minio_file_url: str | None


class AttachmentSchema(BaseSchema, AttachmentMinioSchema):
    '''
    Упрощенная Pydantic-схема медиа-контента, прикрепляемого к теме

    Args:
        id (int): Идентификатор
        block_id (int): Идентификатор блока, \
            к которому принадлежит данный медиа-контент
        tg_msg_id (str): Идентификатор сообщения
        tg_file_url (str): URL файла на серверах telegram
        minio_file_url (str): Ссылка на файл в MinIO
        file_name (str): Имя файла
        file_extension (str): Расширение файла
        file_size (int): Размер файла (байт)
    '''

    block_id: int = Field(gt=0)
