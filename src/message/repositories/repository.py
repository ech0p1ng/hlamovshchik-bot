from base.repository import BaseRepository
from message.models.model import MessageModel
from sqlalchemy.ext.asyncio import AsyncSession


class MessageRepository(BaseRepository[MessageModel]):
    '''Обработка данных сообщений в БД'''

    def __init__(self, db: AsyncSession):
        '''
        Обработка данных сообщений в БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
