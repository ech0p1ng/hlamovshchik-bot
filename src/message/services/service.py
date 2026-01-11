from typing import Any
import async_requests
from attachment.schemas.schema import AttachmentSchema
from config import get_settings
from bs4 import Tag
from bs4 import BeautifulSoup as bs
import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from base.service import BaseService
from message.models.model import MessageModel
from message.schemas.schema import MessageSimpleSchema
from message.repositories.repository import MessageRepository
from attachment.services.service import AttachmentService
from attachment.models.model import AttachmentModel


class MessageService(BaseService[MessageModel]):
    '''
    Бизнес-логика сообщений
    '''

    def __init__(self, db: AsyncSession, attachment_service: AttachmentService):
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
        self.attachment_service = attachment_service
        self.logger = logging.getLogger('tg_logger')
        self.__settings = get_settings()

    async def create(
        self,
        model: MessageModel,
        files_info: list[tuple[str, str]] | None = None
    ) -> MessageModel:
        '''
        Создать сообщение

        Args:
            model (MessageModel): SQL Alchemy модель сообщения
            files_info (list[tuple[str,str]]): Список `ID сообщения` и `URL медиа-контента`

        Returns:
            MessageModel: SQLAlchemy-модель сообщения

        Raises:
            WasNotCreatedError: Не удалось создать сообщение
        '''
        if not files_info:
            return await super().create(model)

        for f in files_info:
            attachments = await self.attachment_service.upload_files(f)
            model.attachments = attachments or []

        return await super().create(model)

    # async def update_all():

    async def __parse_data(self, message: Tag) -> dict[str, Any]:
        message_text = message.select('.tgme_widget_message_text.js-message_text')
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
        return {
            'id': int(message_id),
            'text': message_text[0].getText(),
            'image_urls': image_urls,
        }

    async def __parse_messages(self, after: int | None = None, before: int | None = None) -> list[dict[str, Any]] | None:
        '''
        Парсинг 15 сообщений

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
                if i > 15:
                    break
                parsed_data.append(await self.__parse_data(m))
            return parsed_data

    async def __get_last_msg_id(self) -> int:
        parsed = await self.__parse_messages(before=0)
        if parsed is None:
            raise Exception('Не удалось спарсить сообщения')
        return parsed[-1]['id'] + 10  # 10 с запасом на изображения, которые считаются за отдельные сообщения

    async def __parse_messages_all(self) -> list[dict[str, Any]]:
        '''
        Парсинг всех сообщений из канала

        Raises:
            Exception: Не удалось спарсить сообщения

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
        result = []
        last_msg_id = await self.__get_last_msg_id()
        msg_id = 0
        count = 1

        while msg_id < last_msg_id:
            parsed = await self.__parse_messages(after=count)
            if parsed is not None:
                count += len(parsed)
                for m in parsed:
                    result.append(m)
                    # logger.info(json.dumps(m, ensure_ascii=False, indent=2))
            await asyncio.sleep(random.randint(2, 5))
        return result

    async def update_all(self) -> list[MessageModel]:
        models = []
        self.logger.info('Обновление займет продолжительное время...')
        try:
            messages = await self.__parse_messages_all()
        except Exception as e:
            self.logger.error(f'Произошла ошибка: {str(e)}')
        else:
            for m in messages:
                files: list[tuple[str, str]] = [(m['id'], img) for img in m['image_urls']]
                attachments = await self.attachment_service.upload_files(*files) or []
                schema = MessageSimpleSchema(
                    tg_msg_id=m['id'],
                    text=m['text'],
                    attachments=[AttachmentSchema.model_validate(a) for a in attachments]
                )
                model = MessageModel.from_schema(schema)
                model = await self.create(model)
                models.append(model)
        return models
