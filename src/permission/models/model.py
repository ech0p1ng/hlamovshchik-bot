from sqlalchemy import ForeignKey
from base.model import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from permission.schemas.schema import (
    PermissionSchema, PermissionSimpleSchema
)


class PermissionModel(BaseModel):
    '''
    Таблица для разрыва связи "многие ко многим" у таблиц botcommands и roles
    '''
    __tablename__ = 'permissions'
    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))
    botcommand_id: Mapped[int] = mapped_column(ForeignKey('botcommands.id'))

    @classmethod
    def from_schema(cls, schema: PermissionSimpleSchema | PermissionSchema):
        if type(schema) is PermissionSchema:
            return cls(
                id=schema.id,
                role_id=schema.role_id,
                endpoint_id=schema.botcommand_id
            )
        else:
            return cls(
                role_id=schema.role_id,
                endpoint_id=schema.botcommand_id
            )
