from pydantic import Field
from base.schema import BaseSimpleSchema, BaseSchema


class RoleSimpleSchema(BaseSimpleSchema):
    '''
    Pydantic-модель роли

    Args:
        name (str): Название роли
    '''
    name: str = Field(min_length=2, max_length=16)


class RoleSchema(RoleSimpleSchema, BaseSchema):
    '''
    Pydantic-модель роли

    Args:
        id (int): Идентификатор
        name (str): Название роли
    '''
    pass
