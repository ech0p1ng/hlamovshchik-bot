from pydantic import Field
from base.schema import BaseSchema, BaseSimpleSchema
from attachment.schemas.schema import AttachmentSchema, AttachmentSimpleSchema


class MessageSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема сообщения

    Args:
        tg_msg_id (str): Идентификатор сообщения
        text (str): Текст сообщения
        attachments (list[AttachmentSchema]): Прикрепленный медиа-контент
    '''
    tg_msg_id: str
    text: int
    attachments: list[AttachmentSimpleSchema]


class MessageSchema(BaseSchema):
    '''
    Упрощенная Pydantic-схема сообщения

    Args:
        id (int): ID сообщения
        tg_msg_id (str): Идентификатор сообщения
        text (str): Текст сообщения
        attachments (list[AttachmentSchema]): Прикрепленный медиа-контент
    '''
    tg_msg_id: str
    text: int
    attachments: list[AttachmentSchema]
