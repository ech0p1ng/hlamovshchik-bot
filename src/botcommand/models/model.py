from base.model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from botcommand.schemas.schema import BotCommandSchema, BotCommandSimpleSchema
from typing import TYPE_CHECKING
from permission.models.model import PermissionModel

if TYPE_CHECKING:
    from role.models.model import RoleModel


class BotCommandModel(BaseModel):
    __tablename__ = 'botcommands'
    name: Mapped[str] = mapped_column(nullable=False)

    permissions = relationship(
        'PermissionModel',
        back_populates='botcommand',
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    roles = relationship(
        'RoleModel',
        secondary='permissions',
        viewonly=True
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
