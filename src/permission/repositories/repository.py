from sqlalchemy.ext.asyncio import AsyncSession
from base.repository import BaseRepository
from permission.models.model import PermissionModel


class PermissionRepository(BaseRepository[PermissionModel]):
    '''
    Класс обработки данных об ограничениях по ролям из БД
    '''

    def __init__(self, db: AsyncSession):
        '''
        Класс обработки данных об ограничениях по ролям из БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
