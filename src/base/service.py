from typing import Any, TypeVar
from base.model import BaseModel
from base.repository import BaseRepository
from sqlalchemy import Select, delete, select
from sqlalchemy.orm import selectinload
from exceptions.exception import NotFoundError, WasNotCreatedError
from sqlalchemy.orm.strategy_options import _AttrType


M = TypeVar("M", bound=BaseModel)


class BaseService[M]:
    '''
    Базовый класс для бизнес-логики приложения.

    Generics:
        M: Класс SQLAlchemy-модели
    '''
    model_class: type[M]

    def __init__(
        self,
        repository: BaseRepository,
        model_class: type[M],
        single_model_name: str,
        multiple_models_name: str
    ):
        '''
        Инициализация сервиса

        Args:
            repository (BaseRepository): Репозиторий для работы с базой данных
            model_class (type[M]): Класс SQLAlchemy-модели
            single_model_name (str): Название модели в единственном числе
            multiple_models_name (str): Название модели во множественном числе
        '''
        self.repository = repository
        self.model_class = model_class
        self.single_model_name = single_model_name
        self.multiple_models_name = multiple_models_name

    async def create(self, model: M) -> M:
        '''
        Создать новую сущность в базе данных

        Args:
            model (M): Данные для создания сущности

        Returns:
            M: SQLAlchemy-модель сущности

        Raises:
            WasNotCreatedError: Не удалось создать сущность
        '''
        try:
            model = await self.repository.create(model)
            await self.repository.db.flush()
        except Exception as e:
            await self.repository.db.rollback()
            raise e

        if model is None:
            raise WasNotCreatedError(
                f'Не удалось создать {self.single_model_name}'
            )
        return model

    async def get(
        self,
        filter: dict[str, Any],
        model_attrs: list[_AttrType] = []
    ) -> M:
        '''
        Поиск сущности по идентификатору

        Args:
            filter (dict[str, Any]): Фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`
            model_attrs (list[_AttrType]): Дополнительно подгружаемые сложные \
                аттрибуты SQLAlchemy модели

        Returns:
            M: SQLAlchemy-модель сущности

        Raises:
            NotFoundError: Не удалось найти сущность
        '''

        # Загрузка сложных аттрибутов из БД
        statement = self._add_model_attrs_to_statement(
            select(self.model_class),
            model_attrs
        )

        model = await self.repository.scalar_one_or_none(
            statement.filter_by(**filter)
        )

        await self.repository.db.flush()
        if model is None:
            raise self._not_found_by_filter_error(filter)
        return model

    async def get_multiple(
        self,
        filter: dict[str, Any],
        model_attrs: list[_AttrType] = []
    ) -> list[M]:
        '''
        Поиск сущности по идентификатору

        Args:
            filter (dict[str, Any]): Фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`
            model_attrs (list[_AttrType]): Дополнительно подгружаемые сложные \
                аттрибуты SQLAlchemy модели

        Returns:
            M: SQLAlchemy-модели сущности

        Raises:
            NotFoundError: Не удалось найти сущность
        '''
        # Загрузка сложных аттрибутов из БД
        statement = self._add_model_attrs_to_statement(
            select(self.model_class),
            model_attrs
        )

        models = list(await self.repository.scalar_all(
            statement.filter_by(**filter)
        ))
        await self.repository.db.flush()
        if models is None:
            raise self._not_found_by_filter_error(filter)
        if len(models) == 0:
            raise self._not_found_by_filter_error(filter)

        return models

    async def update(self, model: M, filter: dict[str, Any]) -> M:
        '''
        Обновление существующей сущности

        Args:
            model (M): SQLAlchemy-модель обновляемой сущности
            filter (dict[str, Any]): фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`

        Returns:
            M: SQLAlchemy-модель обновляемой сущности

        Raises:
            NotFoundError: Не удалось найти сущность
        '''

        if not await self.exists(filter):
            raise self._not_found_by_filter_error(filter)

        try:
            model = await self.repository.update(model, filter)
            await self.repository.db.flush()
        except Exception as e:
            await self.repository.db.rollback()
            raise e
        return model

    async def delete(self, filter: dict[str, Any]) -> None:
        '''
        Удаление сущности по идентификатору

        Args:
            filter (dict[str, Any]): фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`

        Raises:
            NotFoundError: Не удалось найти сущность
        '''
        if not await self.exists(filter):
            raise self._not_found_by_filter_error(filter)
        try:
            await self.repository.delete(
                statement=delete(self.model_class),
                filter={"id": id}
            )
            await self.repository.db.flush()
        except Exception as e:
            await self.repository.db.rollback()
            raise e

    async def get_all(self, model_attrs: list[_AttrType] = []):
        '''
        Поиск всех сущностей

        Returns:
            Sequence[M]: Найденные SQLAlchemy-модели сущностей

        Raises:
            NotFoundError: Не удалось найти ни одну сущность
        '''
        statement = self._add_model_attrs_to_statement(
            select(self.model_class),
            model_attrs
        )
        models = await self.repository.scalar_all(statement)
        await self.repository.db.flush()
        if not models:
            raise self._not_found_error_for_list()
        return models

    async def exists(
        self,
        filter: dict[str, Any],
        raise_exc: bool = True
    ) -> bool:
        '''
        Проверка существования сущности в базе данных

        Args:
            filter (dict[str, Any]): Фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`
            raise_exc (bool): Вкл/выкл выбрасывания исключения, \
                если не была найдена сущность

        Returns:
            bool: True - сущность найдена, False - сущность не найдена

        Raises:
            NotFoundError: Не удалось найти сущность по фильтру, \
                если `raise_exc = True`, в противном случае не выбрасывается
        '''

        try:
            found_model = await self.get(filter)
            return bool(found_model)
        except NotFoundError as e:
            if raise_exc:
                raise e
            return False

    def _not_found_error_for_list(self) -> NotFoundError:
        '''
        Возвращает объект NotFoundError с шаблонным сообщением для списка

        Returns:
            NotFoundError: Не найдены несколько сущностей
        '''
        return NotFoundError(
            f'{self.multiple_models_name} не найдены'.capitalize()
        )

    def _not_found_by_filter_error(
        self,
        filter: dict[str, Any]
    ) -> NotFoundError:
        '''
        Возвращает объект NotFoundError с шаблонным сообщением для фильтра

        Args:
            filter (dict[str, Any]): фильтр поиска сущности в БД. \
                `{"Название_атрибута": Значение_атрибута}`

        Returns:
            NotFoundError: Не найдена сущность по фильтру
        '''
        return NotFoundError(
            f'Не был найден объект "{self.single_model_name}" '
            f'по фильтру {filter}'.capitalize()
        )

    def _add_model_attrs_to_statement(
        self,
        statement: Select,
        model_attrs: list[_AttrType] = []
    ) -> Select:
        '''
        Добавление стейтменту связанных атрибутов SQLAlchemy модели
        '''
        if model_attrs:
            options = [selectinload(attr) for attr in model_attrs]
            statement.options(*options)
        return statement
