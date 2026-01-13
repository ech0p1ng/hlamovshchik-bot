from pydantic import Field
from base.schema import BaseSimpleSchema
from role.schemas.schema import RoleSchema


class UserSimpleSchema(BaseSimpleSchema):
    '''
    Упрощенаня pydantic-модель пользователя

    Args:
        id (int): Telegram id (не @username) пользователя
        user_name (str | None): @username
        role_id (int): Идентификатор роли
    '''
    id: int = Field(gt=0)
    # profile_name: str
    user_name: str | None
    role_id: int = Field(gt=0)


class UserSchema(BaseSimpleSchema):
    '''
    Pydantic-модель пользователя

    Args:
        id (int): Telegram id (не @username) пользователя
        user_name (str | None): @username
        role (RoleSchema): Роль
    '''
    id: int = Field(gt=0)
    # profile_name: str
    user_name: str | None
    role: RoleSchema
