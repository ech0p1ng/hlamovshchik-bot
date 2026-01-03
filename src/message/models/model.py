from sqlalchemy.orm import Mapped, mapped_column, relationship
from base.model import BaseModel
from typing import TYPE_CHECKING
from message.schemas.schema import (
    MessageSchema, MessageSimpleSchema
)

if TYPE_CHECKING:
    from attachment.models.model import AttachmentModel


class MessageModel(BaseModel):
    '''
    SQL Alchemy модель сообщения

    Args:
        id (int): Идентификатор
        tg_msg_id (Mapped[str]): Идентификатор сообщения
        text (Mapped[str]): Текст сообщения
        attachment_id (Mapped[int]): ID медиа-контента
    '''
    __tablename__ = 'messages'

    tg_msg_id: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column()

    attachments: Mapped[list['AttachmentModel']] = relationship(
        back_populates='messages',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __eq__(self, value: object) -> bool:

        if isinstance(value, MessageModel):
            self_stats = (
                self.tg_msg_id,
                self.text
            )
            value_stats = (
                value.tg_msg_id,
                value.text
            )
            return self_stats == value_stats
        else:
            return False

    @classmethod
    def from_schema(
        cls,
        schema: MessageSimpleSchema | MessageSchema,
    ) -> 'MessageModel':
        '''
        Получение модели из Pydantic-схем

        Args:
            schema (MessageSimpleSchema | MessageSchema): Pydantic-схема

        Returns:
            MessageModel: SQL Alchemy модель медиафайла
        '''
        from attachment.models.model import AttachmentModel
        return cls(
            tg_msg_id=schema.tg_msg_id,
            text=schema.text,
            attachments=[AttachmentModel.from_schema(attachment)
                         for attachment in schema.attachments]
        )
