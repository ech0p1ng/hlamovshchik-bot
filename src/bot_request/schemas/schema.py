from pydantic import Field
from base.schema import BaseSchema, BaseSimpleSchema
from datetime import datetime, UTC
from user.schemas.schema import UserSchema


class BotRequestCreateSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        user_id (int): Идентификатор пользователя
        user (UserSchema): Pydantic-схема пользователя
        text (str): Текст запроса боту
        sended_pic_url (str): URL отправленного изображения
        send_datetime (datetime): Дата и время отправки запроса боту
    '''
    user_id: int
    user: UserSchema
    text: str
    sended_pic_url: str
    send_datetime: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class BotRequestSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        user_id (int): Идентификатор пользователя
        text (str): Текст запроса боту
        sended_pic_url (str): URL отправленного изображения
        send_datetime (datetime): Дата и время отправки запроса боту
    '''
    user_id: int
    text: str
    sended_pic_url: str
    send_datetime: datetime


class BotRequestSchema(BaseSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        id (int): ID запроса боту
        user_id (int): Идентификатор пользователя
        user (UserSchema): Pydantic-схема пользователя
        text (str): Текст запроса боту
        sended_pic_url (str): URL отправленного изображения
        send_datetime (datetime): Дата и время отправки запроса боту
    '''
    user_id: int
    user: UserSchema
    text: str
    sended_pic_url: str
    send_datetime: datetime
