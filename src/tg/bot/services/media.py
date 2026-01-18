import hashlib
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
from message.models.model import MessageModel
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

    async def find_media(
        self,
        text: str,
        url_type: Literal['global', 'local'],
        reverse: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, str | None]]:
        '''
        Поиск медиа по тексту в канале

        Args:
            text (str): Текст на картинке
            url_type (Literal['global', 'local']): `global` - открытый доступ, `local` - внутри локальной сети
            reversed (bool): В обратном порядке (сначала новые). По-умолчанию - `False`

        Raises:
            NotFoundError: Не удалось найти

        Returns:
            list[dict[str,str|None]]: Список словарей с данными о картинке или сообщение об ошибке
            Словарь:
        ```
        {
            "url": media_url, [str]
            "text": message_text, [str]
            "type": "vid" | "img" | None, [str|None]
            "name": file_name, [str]
            "ext": file_ext, [str]
        }
        ```
        '''
        order_by = MessageModel.id.asc()
        if reverse:
            order_by = MessageModel.id.desc()

        found = await self.message_service.find_with_value(
            filter={'text': text},
            offset=offset,
            limit=limit,
            order_by=order_by
        )

        settings = get_settings()

        result: list[dict[str, str | None]] = []
        for msg in found:
            if url_type == 'local':
                get_url_func = self.minio_service.get_local_file_url
            elif url_type == 'global':
                get_url_func = self.minio_service.get_global_file_url
            else:
                raise AttributeError('Неверный url_type - только local или global')

            media_data = []
            for a in msg.attachments:
                media_data.append(
                    {
                        'url': get_url_func(a.file_name, a.file_extension),
                        'name': a.file_name,
                        'ext': a.file_extension
                    }
                )

            for i, data in enumerate(media_data):
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
                    'name': data['name'],
                    'ext': data['ext'],
                })
        return result

    async def inline_media(self, text: str) -> list[InlineQueryResultPhoto]:
        '''
        Медиа при вводе @bot_name в поле ввода сообщения

        Args:
            text (str): Текст для поиска

        Returns:
            list[InlineQueryResultPhoto]: Найденные изображения

        Raises:
            NotFoundError: Не удалось найти
        '''
        media = []
        found = await self.find_media(text, url_type='global', reverse=True)
        
        for media_data in found:
            if media_data['type'] == 'img':
                photo_url = media_data['url']
                if not photo_url:
                    continue
                title = (media_data['text'] or '')[:64]
                media.append(InlineQueryResultPhoto(
                    id=hashlib.sha1(str(media_data['url']).encode()).hexdigest(),  # уникальный и стабильный id
                    photo_url=photo_url,
                    thumbnail_url=photo_url,
                    title=title,
                    description=f"Отправлено с канала @{get_settings().telegram.channel_name}"
                ))
        return media

    async def inchat_media(self, text: str) -> list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo]:
        '''
        Медиа в чате с ботом

        Args:
            text (str): Текст для поиска

        Returns:
            list[InputMediaAudio|InputMediaDocument|InputMediaPhoto|InputMediaVideo]: Список найденных медиа

        Raises:
            NotFoundError: Ничего не найдено
        '''
        result = []
        found = await self.find_media(text, 'local')
        for media_data in found:
            file_data = await download_file(media_data['url'])  # type: ignore
            file: BytesIO = file_data['file']
            buffered_file = BufferedInputFile(
                file.getvalue(),
                f'{file_data['name']}.{file_data['ext']}'
            )

            media: InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo | None = None
            if media_data['type'] == 'img':
                media = InputMediaPhoto(media=buffered_file)
            elif media_data['type'] == 'vid':
                media = InputMediaVideo(media=buffered_file)

            if media:
                result.append(media)
        return result
