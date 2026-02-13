from base.repository import BaseRepository
from user.models.model import UserModel
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(BaseRepository[UserModel]):
    '''Обработка данных пользователя в БД'''

    def __init__(self, db: AsyncSession):
        '''
        Обработка данных пользователя в БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
