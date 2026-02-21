from base.repository import BaseRepository
from message.models.model import MessageModel
from sqlalchemy.ext.asyncio import AsyncSession


class BotRequestRepository(BaseRepository[MessageModel]):
    '''Обработка запросов боту в БД'''

    def __init__(self, db: AsyncSession):
        '''
        Обработка запросов боту в БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
