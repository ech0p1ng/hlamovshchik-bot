from base.repository import BaseRepository
from attachment.models.model import AttachmentModel
from sqlalchemy.ext.asyncio import AsyncSession


class AttachmentRepository(BaseRepository[AttachmentModel]):
    '''Обработка данных прикрепляемого медиа-контента в БД'''

    def __init__(self, db: AsyncSession):
        '''
        Обработка данных прикрепляемого медиа-контента в БД

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(db)
