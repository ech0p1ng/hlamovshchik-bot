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
from dependencies import (
    get_message_service,
    get_minio_service,
)
from config import get_settings


class MediaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def update_messages_base(self) -> AsyncGenerator[str]:
        '''
        Парсинг всех сообщений в канале

        Yields:
            Iterator[AsyncGenerator[str]]: Прогресс парсинга
        '''
        yield 'Запуск парсинга...'
        show_msg = True
        skipped = set()
        message_service = await get_message_service(self.db)
        try:
            async for msg in message_service.parse_all():
                if show_msg:
                    current = msg['current']
                    skipped.update(msg['skipped'])
                    current_str = ', '.join([str(msg_id) for msg_id in current])
                    skipped_str = ', '.join([str(msg_id) for msg_id in skipped])
                    last = msg['last']
                    first = msg['first']
                    total = msg['total']
                    output = (f'Парсинг...\n\n'
                              f'ID первого: {first}\n'
                              f'ID последнего: {last}\n'
                              f'ID текущих: {current_str}\n' +
                              (f'ID пропущенных: {skipped_str}\n' if skipped else '') +
                              f'Итого сообщений за этот момент: {total}')
                    await self.db.commit()
                    yield output
        except minio.error.S3Error as e:
            msg = e.message or str(e)
            logging.error(msg)
            yield msg

    async def find_media(self, text: str, url_type: Literal['global', 'local']) -> AsyncGenerator[list[dict[str, str | None]]]:
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
        found = []
        message_service = await get_message_service(self.db)
        minio_service = get_minio_service()

        found = await message_service.find_with_value({'text': text})

        settings = get_settings()
        for msg in found:
            get_url_func = minio_service.get_local_file_url if url_type == 'local' else minio_service.get_global_file_url
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

    async def inline_media(self, text: str) -> list[InlineQueryResultPhoto]:
        '''
        Медиа при вводе @bot_name в поле ввода сообщения

        Args:
            text (str): Текст для поиска

        Returns:
            list[InlineQueryResultPhoto]: Найденные изображения
        '''
        results = []
        count = 1
        async for data in self.find_media(text, 'global'):
            for img_data in data:
                if img_data['type'] == 'img':
                    results.append(InlineQueryResultPhoto(
                        id=str(count),
                        photo_url=img_data['url'],  # type: ignore
                        thumbnail_url=img_data['url'],  # type: ignore  # можно уменьшить, но для начала сойдёт
                        title=(img_data['text'] or '')[:64],
                        description="Отправлено с канала Хлам"
                    ))
                    count += 1

        return results

    async def inchat_media(self, text: str) -> AsyncGenerator[list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo]]:
        '''
        Медиа в чате с ботом

        Args:
            text (str): Текст для поиска

        Yields:
            Iterator[AsyncGenerator[list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo]]]: Список найденных медиа
        '''
        async for data in self.find_media(text, 'local'):
            media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo] = []
            for img_data in data:
                file_data = await download_file(img_data['url'])  # type: ignore
                file: BytesIO = file_data['file']
                buffered_file = BufferedInputFile(
                    file.getvalue(),
                    f'{file_data['name']}.{file_data['ext']}'
                )
                if img_data['type'] == 'img':
                    media.append(InputMediaPhoto(media=buffered_file))
                elif img_data['type'] == 'vid':
                    media.append(InputMediaVideo(media=buffered_file))
            yield media
