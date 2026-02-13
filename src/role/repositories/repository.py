from typing import TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from base.repository import BaseRepository
from role.models.model import RoleModel


T = TypeVar("T")


class RoleRepository(BaseRepository[RoleModel]):
    '''
    Класс обработки данных о ролях из БД
    '''

    def __init__(self, db: AsyncSession):
        '''
        Класс обработки данных о ролях из БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
