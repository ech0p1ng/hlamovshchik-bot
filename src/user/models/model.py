from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import ForeignKey
from base.model import BaseModel
from user.schemas.schema import UserSchema, UserSimpleSchema
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot_request.models.model import BotRequestModel
    from role.models.model import RoleModel


class UserModel(BaseModel):
    '''
    SQL Alchemy модель пользователя

    Args:
        id (int): Идентификатор
        user_name (str): @username
        role (RoleModel): Роль
        bot_requests (list[BotRequestModel]): Запросы боту
    '''
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_name: Mapped[str] = mapped_column(nullable=True)

    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'))
    role: Mapped['RoleModel'] = relationship(
        back_populates='users',
        lazy='selectin',
    )
    
    bot_requests: Mapped[list['BotRequestModel']] = relationship(
        'BotRequestModel',
        back_populates='user',
        uselist=True,
        cascade='all, delete-orphan',
        lazy='selectin'
    )

    @classmethod
    def from_schema(
        cls,
        schema: UserSchema | UserSimpleSchema
    ) -> 'UserModel':
        from role.models.model import RoleModel
        from bot_request.models.model import BotRequestModel
        if type(schema) is UserSchema:
            return cls(
                id=schema.id,
                user_name=schema.user_name,
                role=RoleModel.from_schema(schema.role),
                bot_requests=[BotRequestModel.from_schema(br) for br in schema.bot_requests]
            )
        elif type(schema) is UserSimpleSchema:
            return cls(
                id=schema.id,
                user_name=schema.user_name,
                role_id=schema.role_id
            )
        else:
            return cls()
