from pydantic import Field
from base.schema import BaseSimpleSchema, BaseSchema


class PermissionSimpleSchema(BaseSimpleSchema):
    '''
    Pydantic-схема ограничения доступа

    Args:
        role_id (int): Идентификатор роли, которой доступна ручка
        botcommand_id (int): Идентификатор команды бота
    '''
    role_id: int = Field(gt=0)
    botcommand_id: int = Field(gt=0)


class PermissionSchema(BaseSchema, PermissionSimpleSchema):
    '''
    Pydantic-схема ограничения доступа

    Args:
        role_id (int): Идентификатор роли, которой доступна ручка
        botcommand_id (int): Идентификатор команды бота
    '''
