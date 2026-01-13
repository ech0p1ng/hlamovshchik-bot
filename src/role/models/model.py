from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, relationship
from base.model import BaseModel
from role.schemas.schema import RoleSchema, RoleSimpleSchema
from botcommand.models.model import BotCommandModel
from permission.table import permissions_table

if TYPE_CHECKING:
    from user.models.model import UserModel


class RoleModel(BaseModel):
    '''
    Роль

    Args:
        id (int): Идентификатор
        name (str): Название роли

    '''
    __tablename__ = 'roles'
    name: Mapped[str]
    users: Mapped[list['UserModel']] = relationship(
        back_populates='role',
        lazy='selectin',
    )

    botcommands: Mapped[list['BotCommandModel']] = relationship(
        back_populates='roles',
        uselist=True,
        secondary=permissions_table,
        lazy='selectin'
    )

    @classmethod
    def from_schema(cls, schema: RoleSchema | RoleSimpleSchema) -> 'RoleModel':
        if type(schema) is RoleSchema:
            return cls(
                id=schema.id,
                name=schema.name
            )
        else:
            return cls(
                name=schema.name
            )
