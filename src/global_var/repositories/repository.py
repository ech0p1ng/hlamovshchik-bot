from base.repository import BaseRepository
from global_var.models.model import GlobalVarModel
from sqlalchemy.ext.asyncio import AsyncSession


class GlobalVarRepository(BaseRepository[GlobalVarModel]):
    '''Обработка данных глобальных переменных и констант'''

    def __init__(self, db: AsyncSession):
        '''
        Обработка данных глобальных переменных и констант

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
