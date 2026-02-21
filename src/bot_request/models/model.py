from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base.model import BaseModel
from typing import TYPE_CHECKING
from bot_request.schemas.schema import (
    BotRequestCreateSchema, BotRequestSchema, BotRequestSimpleSchema
)

if TYPE_CHECKING:
    from user.models.model import UserModel


class BotRequestModel(BaseModel):
    '''
    SQL Alchemy модель запроса боту

    Args:
        id (int): Идентификатор
        user_id (Mapped[int]): Идентификатор пользователя
        user (Mapped[UserModel]): Пользователь
        text (Mapped[str]): Текст сообщения
        sended_pic_url (Mapped[str]): URL отправленного изображения
        send_datetime (datetime): Дата и время отправки запроса
    '''
    __tablename__ = 'bot_request'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    user: Mapped['UserModel'] = relationship(
        'UserModel',
        backpopulates='bot_requests',
        foreign_keys=[user_id],
        lazy='selectin'
    )

    text: Mapped[str] = mapped_column()

    sended_pic_url: Mapped[str] = mapped_column()
    
    send_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    def __eq__(self, value: object) -> bool:
        if isinstance(value, BotRequestModel):
            self_stats = (
                self.user_id,
                self.text,
                self.sended_pic_url,
            )
            value_stats = (
                value.user_id,
                value.text,
                value.sended_pic_url,
            )
            return self_stats == value_stats
        else:
            return False

    @classmethod
    def from_schema(
        cls,
        schema: BotRequestSchema | BotRequestSchema | BotRequestCreateSchema,
    ) -> 'BotRequestModel':
        '''
        Получение модели из Pydantic-схем

        Args:
            schema (BotRequestSimpleSchema | BotRequestSchema): Pydantic-схема

        Returns:
            BotRequestModel: SQL Alchemy модель запроса
        '''
        from user.models.model import UserModel
        if type(schema) in (BotRequestSimpleSchema, BotRequestSchema):
            return cls(
                tg_msg_id=schema.user_id,
                text=schema.text,
                user=UserModel.from_schema(schema.user)
            )
        elif type(schema) is BotRequestCreateSchema:
            return cls(
                tg_msg_id=schema.user_id,
                text=schema.text,
            )
        return cls()
