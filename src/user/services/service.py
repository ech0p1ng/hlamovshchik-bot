import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AttrType

from base.service import BaseService
from user.repositories.repository import UserRepository
from user.models.model import UserModel
from role.services.service import RoleService
from user.schemas.schema import UserSimpleSchema
from permission.services.service import PermissionService

FORBIDDEN_MSG = 'Доступ запрещен'


class UserService(BaseService[UserModel]):
    '''
    Бизнес-логика пользователя
    '''

    def __init__(self, db: AsyncSession, permission_service: PermissionService):
        '''
        Бизнес-логика пользователя

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            UserRepository(db),
            UserModel,
            single_model_name="пользователь",
            multiple_models_name="пользователи"
        )
        self.role_service = RoleService(db)
        self.permission_service = permission_service

    async def get_all(
        self,
        model_attrs: list[_AttrType] = [
            UserModel.role
        ]
    ):
        '''
        Поиск всех сущностей

        Returns:
            Sequence[M]: Найденные SQLAlchemy-модели сущностей

        Raises:
            NotFoundError: Не удалось найти ни одну сущность
        '''
        return await super().get_all(model_attrs)

    async def get(
        self,
        filter: dict[str, Any],
        model_attrs: list[_AttrType] = [
            UserModel.role
        ]
    ) -> UserModel:
        '''
        Поиск пользователя по идентификатору

        Args:
            filter (dict[str, Any]): Фильтр поиска пользователя в БД. \
                `{"Название_атрибута": Значение_атрибута}`
            model_attrs (list[_AttrType]): Список атрибутов модели, \
                необходимых для подгрузки из БД

        Returns:
            UserModel: SQLAlchemy-модель пользователя

        Raises:
            NotFoundError: Не удалось найти пользователя
        '''
        return await super().get(filter, model_attrs)

    async def get_by_id_and_name(self, id: int, username: str | None) -> UserModel:
        '''
        Получить пользователя по его id и username

        Raises:
            RuntimeError: get_db() did not yield a session

        Returns:
            UserModel: SQLAlchemy модель пользователя
        '''
        filter = {'id': id}
        user: UserModel | None = None
        if not await self.exists(filter, raise_exc=False):
            await self.create(UserModel.from_schema(
                UserSimpleSchema(id=id, user_name=username, role_id=2)
            ))
        user = await self.get(filter, [UserModel.role])
        if not user:
            raise RuntimeError("Пользователь не был создан")
        return user

    async def create(self, model: UserModel) -> UserModel:
        '''
        Создать новую сущность в базе данных

        Args:
            model (UserModel): Данные для создания пользователя

        Returns:
            UserModel: SQLAlchemy-модель пользователя

        Raises:
            WasNotCreatedError: Не удалось создать сущность
            NotFoundError: Не удалось найти роль
            AlreadyExistsError: Пользователь уже существует
        '''
        await self.role_service.exists({"id": model.role_id})
        return await super().create(model)

    async def check_permission(self, command: str, id: int, username: str | None) -> tuple[bool, str]:
        '''
        Проверка доступа пользователя

        Args:
            command (str): Отправленная команда без /
            message (types.Message): Отправленное пользователем сообщение

        Returns:
            tuple[bool, str]: Разрешить/запретить доступ; ответ бота
        '''
        user = await self.get_by_id_and_name(id, username)
        permitted = await self.permission_service.check_permission(
            command, user, raise_exc=False
        )
        return (permitted, '' if permitted else FORBIDDEN_MSG)
