from typing import Any
from user.repositories.repository import UserRepository
from base.service import BaseService
from user.models.model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AttrType
from role.services.service import RoleService


class UserService(BaseService[UserModel]):
    '''
    Бизнес-логика пользователя
    '''

    def __init__(self, db: AsyncSession):
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
