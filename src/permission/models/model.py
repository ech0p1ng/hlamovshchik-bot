from sqlalchemy import ForeignKey
from base.model import BaseSimpleModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from permission.schemas.schema import (
    PermissionSchema, PermissionSimpleSchema
)


class PermissionModel(BaseSimpleModel):
    '''
    Таблица для разрыва связи "многие ко многим" у таблиц botcommands и roles
    '''
    __tablename__ = 'permissions'
    role_id: Mapped[int] = mapped_column(
        ForeignKey('roles.id'),
        primary_key=True
    )
    botcommand_id: Mapped[int] = mapped_column(
        ForeignKey('botcommands.id'),
        primary_key=True
    )

    role = relationship(
        'RoleModel',
        back_populates='permissions'
    )

    botcommand = relationship(
        'BotCommandModel',
        back_populates='permissions'
    )

    @classmethod
    def from_schema(cls, schema: PermissionSimpleSchema | PermissionSchema):
        if type(schema) is PermissionSchema:
            return cls(
                id=schema.id,
                role_id=schema.role_id,
                botcommand_id=schema.botcommand_id
            )
        else:
            return cls(
                role_id=schema.role_id,
                botcommand_id=schema.botcommand_id
            )
