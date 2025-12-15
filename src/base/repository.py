from typing import Any, TypeVar
from sqlalchemy import ScalarResult, Select, Delete
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from base.model import BaseModel


T = TypeVar("T", bound=BaseModel)


class BaseRepository[T: BaseModel]:
    '''
    Базовый класс обработки данных из БД

    Attributes:
        T (Any): Класс SQLAlchemy-модели сущности

    Args:
        db (AsyncSession): Асинхронная сессия базы данных
    '''

    def __init__(self, db: AsyncSession):
        self.db = db

    async def scalar_all(self, statement: Select[tuple[T]]) -> Sequence[T]:
        return (await self.db.execute(statement)).scalars().all()

    async def scalar_first(self, statement: Select) -> T | None:
        return (await self.db.execute(statement)).scalars().first()

    async def scalar_one(self, statement: Select) -> T:
        return (await self.db.execute(statement)).scalars().one()

    async def scalar_one_or_none(
        self,
        statement: Select
    ) -> T | None:
        return (await self.db.execute(statement)).scalars().one_or_none()

    async def scalar_unique(
        self,
        statement: Select
    ) -> ScalarResult[T] | None:
        return (await self.db.execute(statement)).scalars().unique()

    async def create(self, model: T) -> T:
        '''
        Добавление сущности

        Args:
            model (T): SQLAlchemy-модель сущности с обновленными данными

        Returns:
            T: модель с обновленными данными
        '''
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return model

    async def update(
        self,
        model: T,
        filter: dict[str, Any]
    ) -> T:
        '''
        Обновление сущности

        Args:
            model (T): SQLAlchemy-модель сущности с обновленными данными
            filter (dict[str, Any]): фильтр поиска сущности в БД \
                `{"Название_атрибута": Значение_атрибута}`

        Returns:
            T: модель с обновленными данными

        Raises:
            ValueError: Неверный фильтр поиска
        '''
        self.check_filters(filter)
        merged = await self.db.merge(model)
        await self.db.flush()
        await self.db.refresh(merged)
        return merged

    async def delete(self, statement: Delete, filter: dict[str, Any]) -> None:
        '''
        Удаление сущности из базы данных

        Args:
            filter (dict[str, Any]): фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`

        Raises:
            NotFoundError: Не удалось найти сущность
            ValueError: Неверный фильтр поиска
        '''
        self.check_filters(filter)
        await self.db.execute(statement)
        await self.db.flush()

    def check_filters(self, filter: dict[str, Any]) -> bool:
        '''
        Проверка фильтра поиска

        Args:
            filter (dict[str, Any]): фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`
        Raises:
            ValueError: Некорректный фильтр поиска
        '''
        if filter is None:
            raise ValueError(
                'Фильтр поиска должен включать в себя хотя бы одну пару '
                '{"Название_атрибута": Значение_атрибута}'
            )
        return True
