from io import BytesIO
from aiogram.types import (
    BufferedInputFile,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
    InlineQueryResultPhoto,
)
from typing import Any, AsyncGenerator, Literal
import minio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from async_requests import download_file
from config import get_settings
from message.services.service import MessageService
from storage.services.minio_service import MinioService
from exceptions.exception import NotFoundError


class MediaService:
    def __init__(self, db: AsyncSession, message_service: MessageService, minio_service: MinioService) -> None:
        self.db = db
        self.message_service = message_service
        self.minio_service = minio_service

    def __get_msg_url(self, msg_id: int) -> str:
        settings = get_settings()
        return f'https://t.me/{settings.telegram.channel_name}/{msg_id}'

    async def update_messages_base(self, show_msg=False) -> AsyncGenerator[str, None]:
        '''
        Парсинг всех сообщений в канале

        Args:
            show_msg (bool): Выводить спаршеные сообщения отправителю. По-умолчанию `False`

        Yields:
            Iterator[AsyncGenerator[str]]: Прогресс парсинга
        '''
        yield 'Запуск парсинга...'
        skipped = set()

        try:
            async for msg in self.message_service.parse_new():
                if show_msg:
                    current = msg['current']
                    skipped.update(msg['skipped'])
                    current_str = '\n'.join([self.__get_msg_url(msg_id) for msg_id in current])
                    skipped_str = '\n'.join([self.__get_msg_url(msg_id) for msg_id in skipped])
                    last = msg['last']
                    first = msg['first']
                    total = msg['total']
                    output = (f'Парсинг...\n\n'
                              f'Первое: {self.__get_msg_url(first)}\n'
                              f'Последнее: {self.__get_msg_url(last)}\n'
                              f'Текущие:\n{current_str}\n' +
                              (f'Пропущенные:\n{skipped_str}\n' if skipped else '') +
                              f'Итого сообщений за этот момент: {total}')
                    await self.db.commit()
                    yield output
        except minio.error.S3Error as e:
            message = e.message or str(e)
            logging.error(message)
            yield message
        yield 'Парсинг завершен'

    async def find_media(self, text: str, url_type: Literal['global', 'local'], reverse: bool = False) -> AsyncGenerator[list[dict[str, str | None]], None]:
        '''
        Поиск медиа по тексту в канале

        Args:
            text (str): Текст на картинке
            url_type (Literal['global', 'local']): `global` - открытый доступ, `local` - внутри локальной сети
            reversed (bool): В обратном порядке (сначала новые). По-умолчанию - `False`

        Yields:
            Iterator[AsyncGenerator[list[dict[str,str|None]]]]: Список словарей с данными о картинке или сообщение об ошибке
            Словарь:
        ```
        {
            "url": media_url, [str]
            "text": message_text, [str]
            "type": "vid" | "img" | None, [str|None]
        }
        ```
        '''
        found = await self.message_service.find_with_value({'text': text})
        if reverse:
            found.reverse()

        if not found:
            return
            # raise NotFoundError('Ничего не найдено')

        settings = get_settings()

        for msg in found:
            if url_type == 'local':
                get_url_func = self.minio_service.get_local_file_url
            elif url_type == 'global':
                get_url_func = self.minio_service.get_global_file_url
            else:
                raise AttributeError('Неверный url_type - только local или global')

            img_data = []
            for a in msg.attachments:
                img_data.append(
                    {
                        'url': get_url_func(a.file_name, a.file_extension),
                        'name': a.file_name,
                        'ext': a.file_extension
                    }
                )

            result: list[dict[str, str | None]] = []
            for i, data in enumerate(img_data):
                if i == 10:
                    break
                file_type = None
                if data['ext'] in settings.attachment.image_extensions:
                    file_type = 'img'
                elif data['ext'] in settings.attachment.video_extensions:
                    file_type = 'vid'
                result.append({
                    'text': msg.text,
                    'url': data['url'],
                    'type': file_type,
                })
            yield result

    async def inline_media(self, text: str) -> AsyncGenerator[list[InlineQueryResultPhoto]]:
        '''
        Медиа при вводе @bot_name в поле ввода сообщения

        Args:
            text (str): Текст для поиска

        Yields:
            list[InlineQueryResultPhoto]: Найденные изображения

        Raises:
            NotFoundError: Ничего не найдено
        '''
        async for data in self.find_media(text, url_type='global', reverse=True):
            media = []
            for img_data in data:
                if img_data['type'] == 'img':
                    photo_url = img_data['url']
                    if photo_url:
                        title = (img_data['text'] or '')[:64]
                        media.append(InlineQueryResultPhoto(
                            id=str(uuid.uuid4()),
                            photo_url=photo_url,
                            thumbnail_url=photo_url,
                            title=title,
                            description="Отправлено с канала Хлам"
                        ))
            yield media

    async def inchat_media(self, text: str) -> AsyncGenerator[list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo], None]:
        '''
        Медиа в чате с ботом

        Args:
            text (str): Текст для поиска

        Yields:
            Iterator[AsyncGenerator[list[InputMediaAudio|InputMediaDocument|InputMediaPhoto|InputMediaVideo]]]: Список найденных медиа

        Raises:
            NotFoundError: Ничего не найдено
        '''
        async for all_media_data in self.find_media(text, 'global'):
            result = []
            for media_data in all_media_data:
                media = None
                file_url = str(media_data['url'])

                if media_data['type'] == 'img':
                    media = InputMediaPhoto(media=file_url)
                elif media_data['type'] == 'vid':
                    media = InputMediaVideo(media=file_url)

                if media:
                    result.append(media)
            yield result
