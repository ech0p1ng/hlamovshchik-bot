from pydantic import Field
from base.schema import BaseSchema, BaseSimpleSchema
from datetime import datetime, UTC


class BotRequestCreateSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        user_id (int): Идентификатор пользователя
        text (str): Текст запроса боту
        send_datetime (datetime): Дата и время отправки запроса боту
        request_type (str): Тип запроса (inline, chat и т.п.)
    '''
    user_id: int
    text: str
    # sended_pic_url: str
    send_datetime: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    request_type: str


class BotRequestSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        user_id (int): Идентификатор пользователя
        text (str): Текст запроса боту
        request_type (str): Тип запроса (inline, chat и т.п.)
    '''
    user_id: int
    text: str
    request_type: str
    send_datetime: datetime


class BotRequestSchema(BaseSchema):
    '''
    Упрощенная Pydantic-схема запроса боту

    Args:
        id (int): ID запроса боту
        user_id (int): Идентификатор пользователя
        text (str): Текст запроса боту
        request_type (str): Тип запроса (inline, chat и т.п.)
    '''
    user_id: int
    text: str
    request_type: str
    send_datetime: datetime
