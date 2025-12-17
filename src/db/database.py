from typing import AsyncGenerator
from attachment.models.model import AttachmentModel
from config import settings
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)


async_engine = create_async_engine(settings.postgres.db_dsn, echo=False)
async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    '''
    Генератор асинхронной сессии.

    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных,
    автоматически обрабатывая коммит, откат транзакций и закрытие сессии.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy для работы с БД

    Raises:
        Exception: Любое исключение, возникшее при работе с сессией,
                  приводит к откату транзакции
    '''
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
