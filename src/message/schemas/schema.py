from pydantic import Field
from base.schema import BaseSchema, BaseSimpleSchema
from attachment.schemas.schema import AttachmentSchema, AttachmentSimpleSchema


class MessageCreateSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема сообщения

    Args:
        tg_msg_id (int): Идентификатор сообщения
        text (str): Текст сообщения
    '''
    tg_msg_id: int
    text: str


class MessageSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема сообщения

    Args:
        tg_msg_id (int): Идентификатор сообщения
        text (str): Текст сообщения
        attachments (list[AttachmentSchema] | list): Прикрепленный медиа-контент
    '''
    tg_msg_id: int
    text: str
    attachments: list[AttachmentSimpleSchema] | list


class MessageSchema(BaseSchema):
    '''
    Упрощенная Pydantic-схема сообщения

    Args:
        id (int): ID сообщения
        tg_msg_id (int): Идентификатор сообщения
        text (str): Текст сообщения
        attachments (list[AttachmentSchema] | None): Прикрепленный медиа-контент
    '''
    tg_msg_id: int
    text: str
    attachments: list[AttachmentSchema] | list
