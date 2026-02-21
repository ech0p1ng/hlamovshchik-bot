from typing import Any

from sqlalchemy import UnaryExpression
from config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy.orm.strategy_options import _AttrType

from base.service import BaseService
from bot_request.models.model import BotRequestModel
from bot_request.repositories.repository import BotRequestRepository


class BotRequestService(BaseService[BotRequestModel]):
    '''
    Бизнес-логика запросов боту
    '''

    def __init__(self, db: AsyncSession):
        '''
        Бизнес-логика запросов боту

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            BotRequestRepository(db),
            BotRequestModel,
            single_model_name="запрос боту",
            multiple_models_name="запросы боту"
        )
        self.db = db
        self.logger = logging.getLogger('tg_logger')

    async def create(
        self,
        model: BotRequestModel,
    ) -> BotRequestModel:
        '''
        Создать сообщение

        Args:
            model (BotRequestModel): SQL Alchemy модель запроса боту

        Returns:
            BotRequestModel: SQLAlchemy-модель запроса боту

        Raises:
            WasNotCreatedError: Не удалось создать сообщение
        '''
        # model.attachments = []
        filter = {
            'user_id': model.user_id,
            'text': model.text,
            
        }
        if await self.exists(filter, raise_exc=False):
            existing = await self.get(filter)
            existing.text = model.text
            existing.user_id = model.user_id
            model = await super().update(existing, filter)
        else:
            model = await super().create(model)
        # if files_info:
        #     attachments = await self.attachment_service.upload_files(*files_info)
        #     model.attachments = attachments or []
        #     await super().update(model, filter)

        return model

    async def find_with_value(
        self,
        filter: dict[str, Any],
        offset: int = 0,
        limit: int = 0,
        order_by: UnaryExpression | None = None,
        model_attrs: list[_AttrType] = [BotRequestModel.user],
    ) -> list[BotRequestModel]:
        '''
            list[BaseModel]: Список найденных сущностей с подгруженными аттрибутами.
        '''
        '''
        Поиск запросов боту с подгрузкой медиа, если это необходимо.
        
        Args:
            filter (dict[str, Any]): Фильтр для поиска сущности в БД.
            offset (int, optional): Сдвиг начала. По умолчанию: `0`.
            limit (int, optional): Ограничение количества. По умолчанию: `0`.
            order_by (UnaryExpression | None, optional): Аттрибут для сортировки. По умолчанию: `None`.
            model_attrs (list[_AttrType], optional): Список SQLAlchemy-атрибутов для подгрузки медиа. По умолчанию: `[BotRequestModel.user]`.
        
        Returns:
            list[BotRequestModel]: _description_.
        '''
        return await super().find_with_value(
            filter=filter,
            offset=offset,
            limit=limit,
            order_by=order_by,
            model_attrs=model_attrs,
        )
