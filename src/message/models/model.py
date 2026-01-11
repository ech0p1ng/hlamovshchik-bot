from sqlalchemy.orm import Mapped, mapped_column, relationship
from base.model import BaseModel
from typing import TYPE_CHECKING
from message.schemas.schema import (
    MessageCreateSchema, MessageSchema, MessageSimpleSchema
)

if TYPE_CHECKING:
    from attachment.models.model import AttachmentModel


class MessageModel(BaseModel):
    '''
    SQL Alchemy модель сообщения

    Args:
        id (int): Идентификатор
        tg_msg_id (Mapped[int]): Идентификатор сообщения
        text (Mapped[str]): Текст сообщения
        attachment_id (Mapped[int]): ID медиа-контента
    '''
    __tablename__ = 'message'

    tg_msg_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    text: Mapped[str] = mapped_column()

    attachments: Mapped[list['AttachmentModel']] = relationship(
        'AttachmentModel',
        back_populates='message',
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
        schema: MessageSimpleSchema | MessageSchema | MessageCreateSchema,
    ) -> 'MessageModel':
        '''
        Получение модели из Pydantic-схем

        Args:
            schema (MessageSimpleSchema | MessageSchema): Pydantic-схема

        Returns:
            MessageModel: SQL Alchemy модель медиафайла
        '''
        from attachment.models.model import AttachmentModel
        if type(schema) in (MessageSimpleSchema, MessageSchema):
            return cls(
                tg_msg_id=schema.tg_msg_id,
                text=schema.text,
                attachments=[AttachmentModel.from_schema(a) for a in schema.attachments]  # type: ignore
            )
        elif type(schema) is MessageCreateSchema:
            return cls(
                tg_msg_id=schema.tg_msg_id,
                text=schema.text,
                attachments=[]
            )
        return cls()
