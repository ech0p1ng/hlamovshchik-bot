from base.model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from botcommand.schemas.botcommand import BotCommandSchema, BotCommandSimpleSchema
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from role.models.model import RoleModel


class BotCommandModel(BaseModel):
    __tablename__ = 'botcommands'
    name: Mapped[str] = mapped_column(nullable=False)

    roles: Mapped[list['RoleModel']] = relationship(
        back_populates='botcommands',
        uselist=True,
        secondary='permission',
        lazy='selectin'
    )

    @classmethod
    def from_schema(cls, schema: BotCommandSimpleSchema | BotCommandSchema):
        if type(schema) is BotCommandSchema:
            return cls(
                id=schema.id,
                name=schema.name
            )
        else:
            return cls(
                name=schema.name
            )
