from typing import Any, AsyncGenerator
import async_requests
from attachment.schemas.schema import AttachmentSchema
from base.model import BaseModel
from config import get_settings
from bs4 import Tag
from bs4 import BeautifulSoup as bs
import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from sqlalchemy.orm.strategy_options import _AttrType

from base.service import BaseService
from message.models.model import MessageModel
from message.schemas.schema import MessageCreateSchema
from message.repositories.repository import MessageRepository
from attachment.services.service import AttachmentService
from attachment.models.model import AttachmentModel
from exceptions.exception import NotFoundError
from global_var.services.service import GlobalVarService


class MessageService(BaseService[MessageModel]):
    '''
    Бизнес-логика сообщений
    '''

    def __init__(self, db: AsyncSession, attachment_service: AttachmentService, global_var_service: GlobalVarService):
        '''
        Бизнес-логика сообщений

        Args:
            db (AsyncSession): Асинхронная сессия БД
        '''
        super().__init__(
            MessageRepository(db),
            MessageModel,
            single_model_name="сообщение",
            multiple_models_name="сообщения"
        )
        self.db = db
        self.attachment_service = attachment_service
        self.global_var_service = global_var_service
        self.logger = logging.getLogger('tg_logger')
        self.__settings = get_settings()
        self.__parsed_messages_at_once = 15

    async def create(
        self,
        model: MessageModel,
        files_info: list[tuple[int, str]] | None = None
    ) -> MessageModel:
        '''
        Создать сообщение

        Args:
            model (MessageModel): SQL Alchemy модель сообщения
            files_info (list[tuple[int,str]]): Список `ID сообщения` и `URL медиа-контента`

        Returns:
            MessageModel: SQLAlchemy-модель сообщения

        Raises:
            WasNotCreatedError: Не удалось создать сообщение
        '''
        # model.attachments = []
        filter = {'tg_msg_id': model.tg_msg_id}
        if await self.exists(filter, raise_exc=False):
            existing = await self.get(filter)
            existing.text = model.text
            existing.attachments = model.attachments
            model = await super().update(existing, filter)
        else:
            model = await super().create(model)
        if files_info:
            attachments = await self.attachment_service.upload_files(*files_info)
            model.attachments = attachments or []
            await super().update(model, filter)

        return model

    async def __parse_data(self, message: Tag) -> dict[str, Any]:
        message_text_arr = message.select('.tgme_widget_message_text.js-message_text')
        message_id = (
            str(
                message
                .select(
                    '.tgme_widget_message.text_not_supported_wrap.js-widget_message',
                    limit=1
                )[0]
                .get('data-post')
            ).replace(f'{self.__settings.telegram.channel_name}/', ''))
        media = message.select('a.tgme_widget_message_photo_wrap')
        image_urls = []
        for m in media:
            style_attr = m.get('style')
            styles = str(style_attr).split(';')
            for s in styles:
                if s.startswith('background-image:url('):
                    url = s.replace("background-image:url('", '')[:-2]
                    image_urls.append(url)
        text = message_text_arr[0].getText() if message_text_arr else ''
        return {
            'id': int(message_id),
            'text': text,
            'image_urls': image_urls,
        }

    async def __parse_messages(self, after: int | None = None, before: int | None = None) -> list[dict[str, Any]] | None:
        '''
        Парсинг сообщений

        Args:
            after (int, optional): ID поста, после которого будут спаршены сообщения. По-умолчанию: None.
            before (int, optional): ID поста, до которого будут спаршены сообщения. По-умолчанию: None.

        Returns:
            list[dict[str,Any]]: Спаршенные сообщения в формате 
        ```
        [
            {
                "id": message_id,
                "text": message_text,
                "image_urls": [image_urls]
            }
        ]
            ```
        '''
        if before is not None and after is not None:
            raise ValueError('Нельзя одновременно использовать before и after')

        base_url = f'https://t.me/s/{self.__settings.telegram.channel_name}'

        if after is not None:
            url = f'{base_url}?after={after}'
        elif before is not None:
            url = f'{base_url}?before={before}'
        else:
            url = base_url

        try:
            response = await async_requests.get(url)
        except Exception as e:
            raise e
        else:
            soup = bs(response.text, 'html.parser')
            messages = soup.select('.tgme_widget_message_wrap.js-widget_message_wrap')
            parsed_data = []
            for i, m in enumerate(messages):
                if i > self.__parsed_messages_at_once:
                    break
                data = await self.__parse_data(m)
                if data['text'] != '':
                    parsed_data.append(data)
            return parsed_data

    async def __get_last_msg_id(self) -> int:
        parsed = await self.__parse_messages(before=0)
        if parsed is None:
            raise Exception('Не удалось спарсить сообщения')
        return parsed[-1]['id'] + 10  # 10 с запасом на изображения, которые считаются за отдельные сообщения

    async def __get_last_parsed_msg_id(self) -> int:
        value = await self.global_var_service.get_value('last_parsed_msg_id') or 1
        return int(value)

    async def __set_last_parsed_msg_id(self, value: int) -> None:
        await self.global_var_service.set_value('last_parsed_msg_id', str(value))

    async def parse(self, first_msg_id: int, last_msg_id: int) -> AsyncGenerator[dict[str, Any]]:
        '''
        Парсинг сообщений из канала

        Raises:
            Exception: Не удалось спарсить сообщения

        Yields:
            dict[str,Any]: Прогресс парсинга 
        ```
        {
            "current": current_msgs_ids, [list[int]]
            "first": first_msg_id, [int]
            "last": last_msg_id, [int]
            "messages": messages, [list[MessageModel]]
            "skipped": messages, [list[int]]
            "total": messages_count [int]
        }
        ```
        '''
        self.logger.info('Обновление займет продолжительное время...')
        while first_msg_id < last_msg_id:
            parsed = await self.__parse_messages(after=first_msg_id)
            models = []
            skipped_messages_id: set[int] = set()

            if parsed:
                current_messages_id = []
                for m in parsed:
                    id = int(m['id'])

                    try:
                        files: list[tuple[int, str]] = [(id, img_url) for img_url in m['image_urls']]
                        schema = MessageCreateSchema(
                            tg_msg_id=id,
                            text=m['text'],
                        )
                        model = await self.create(
                            model=MessageModel.from_schema(schema),
                            files_info=files
                        )
                        models.append(model)
                        current_messages_id.append(id)
                    except Exception:
                        skipped_messages_id.update([id])

                first_msg_id = int(current_messages_id[-1]) + 1
                await self.__set_last_parsed_msg_id(first_msg_id)
                total = len(models)

                yield {
                    'current': current_messages_id,
                    'first': int(first_msg_id),
                    'last': int(last_msg_id),
                    'messages': models,
                    'skipped': skipped_messages_id,
                    'total': total,
                }
            await asyncio.sleep(random.randint(2, 5))

    async def parse_all(self) -> AsyncGenerator[dict[str, Any]]:
        '''
        Парсинг всех сообщений из канала

        Raises:
            Exception: Не удалось спарсить сообщения

        Yields:
            dict[str,Any]: Прогресс парсинга 
        ```
        {
            "current": current_msgs_ids, [list[int]]
            "first": first_msg_id, [int]
            "last": last_msg_id, [int]
            "messages": messages, [list[MessageModel]]
            "skipped": messages, [list[int]]
            "total": messages_count [int]
        }
        ```
        '''
        self.logger.info('Обновление займет продолжительное время...')
        last_msg_id = await self.__get_last_msg_id()
        first_msg_id = 0
        async for msg in self.parse(first_msg_id, last_msg_id):
            yield msg

    async def parse_new(self) -> AsyncGenerator[dict[str, Any]]:
        '''
        Парсинг новых сообщений из канала

        Raises:
            Exception: Не удалось спарсить сообщения

        Yields:
            dict[str,Any]: Прогресс парсинга 
        ```
        {
            "current": current_msgs_ids, [list[int]]
            "first": first_msg_id, [int]
            "last": last_msg_id, [int]
            "messages": messages, [list[MessageModel]]
            "skipped": messages, [list[int]]
            "total": messages_count [int]
        }
        ```
        '''
        self.logger.info('Обновление займет продолжительное время...')
        last_msg_id = await self.__get_last_msg_id()
        first_msg_id = await self.__get_last_parsed_msg_id()
        async for msg in self.parse(first_msg_id, last_msg_id):
            yield msg

    async def find_with_value(
        self,
        filter: dict[str, Any],
        model_attrs: list[_AttrType] = [MessageModel.attachments]
    ) -> list[MessageModel]:
        try:
            return await super().find_with_value(filter, model_attrs)
        except NotFoundError:
            return []
