from sqlalchemy.ext.asyncio import AsyncSession
from botcommand.models.model import BotCommandModel
from base.repository import BaseRepository


class EndpointRepository(BaseRepository[BotCommandModel]):
    '''
    Класс обработки данных о ручках из БД
    '''

    def __init__(self, db: AsyncSession):
        '''
        Класс обработки данных о ручках из БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
