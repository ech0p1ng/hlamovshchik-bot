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

    async def update_messages_base(self) -> AsyncGenerator[str, None]:
        '''
        Парсинг всех сообщений в канале

        Yields:
            Iterator[AsyncGenerator[str]]: Прогресс парсинга
        '''
        yield 'Запуск парсинга...'
        show_msg = True
        skipped = set()

        try:
            async for msg in self.message_service.parse_all():
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

    async def find_media(self, text: str, url_type: Literal['global', 'local']) -> AsyncGenerator[list[dict[str, str | None]], None]:
        '''
        Поиск медиа по тексту в канале

        Args:
            text (str): Текст на картинке

        Yields:
            Iterator[AsyncGenerator[list[dict[str,str|None]]]]: Список словарей с данными о картинке или сообщение об ошибке
            Словарь:
        ```
        {
            "text": message_text, [str]
            "url": img_url, [str]
            "type": "vid" | "img" | None, [str|None]
        }
        ```
        '''
        found = await self.message_service.find_with_value({'text': text})

        if not found:
            raise NotFoundError('Ничего не найдено')

        settings = get_settings()
        for msg in found:
            get_url_func = self.minio_service.get_local_file_url if url_type == 'local' else self.minio_service.get_global_file_url
            img_data = [{'url': get_url_func(a.file_name, a.file_extension), 'name': a.file_name, 'ext': a.file_extension}
                        for a in msg.attachments]
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
        count = 1
        async for data in self.find_media(text, 'global'):
            media = []
            for img_data in data:
                if img_data['type'] == 'img':
                    media.append(InlineQueryResultPhoto(
                        id=str(count),
                        photo_url=img_data['url'],  # type: ignore
                        thumbnail_url=img_data['url'],  # type: ignore  # можно уменьшить, но для начала сойдёт
                        title=(img_data['text'] or '')[:64],
                        description="Отправлено с канала Хлам"
                    ))
                    count += 1
            yield media

    async def inchat_media(self, text: str) -> AsyncGenerator[list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo], None]:
        '''
        Медиа в чате с ботом

        Args:
            text (str): Текст для поиска

        Yields:
            Iterator[AsyncGenerator[list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo]]]: Список найденных медиа

        Raises:
            NotFoundError: Ничего не найдено
        '''
        async for data in self.find_media(text, 'local'):
            media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo] = []
            for i, img_data in enumerate(data):
                file_data = await download_file(img_data['url'])  # type: ignore
                file: BytesIO = file_data['file']
                buffered_file = BufferedInputFile(
                    file.getvalue(),
                    f'{file_data['name']}.{file_data['ext']}'
                )

                kwargs = {}
                if i == 0:
                    file_name = file_data['name']
                    file_ext = file_data['ext']
                    url_global = self.minio_service.get_global_file_url(file_name, file_ext)
                    kwargs['caption'] = url_global

                if img_data['type'] == 'img':
                    media.append(InputMediaPhoto(media=buffered_file))
                elif img_data['type'] == 'vid':
                    media.append(InputMediaVideo(media=buffered_file))
            yield media
