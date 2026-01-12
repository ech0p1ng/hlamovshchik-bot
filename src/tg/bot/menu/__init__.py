from functools import partial
from io import BytesIO
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio

from async_requests import download_file
from dependencies import get_message_service, get_minio_service
from db.database import get_db
from config import get_settings

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")


@router.message(Command("parse"))
async def update_messages_base(message: types.Message):
    await message.answer('Запуск парсинга...')
    show_msg = True
    async for db in get_db():
        message_service = await get_message_service(db)
        async for msg in message_service.upload_all():
            if show_msg:
                current = msg['current']
                last = msg['last']
                total = msg['total']
                output = (f'Парсинг...\n\n'
                          f'Текущее: ID {current}\n'
                          f'Последнее: ID {last}\n'
                          f'Кол-во сообщений за этот момент: {total}')
                await message.answer(output)


@router.message(Command("find"))
async def find_message(message: types.Message):
    if not message.text:
        await message.reply("Пожалуйста, укажите текст для поиска.")
        return

    query_text = message.text[len("/find "):].strip()

    if not query_text:
        await message.reply("Пожалуйста, укажите текст для поиска.")
        return

    found = []
    async for db in get_db():
        message_service = await get_message_service(db)
        found = await message_service.find_with_value({'text': query_text})

    minio_service = get_minio_service()
    settings = get_settings()
    for msg in found:
        img_urls = [minio_service.get_local_file_url(a.file_name, a.file_extension)
                    for a in msg.attachments]
        media: list[InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo] = []
        for i, url in enumerate(img_urls):
            if i == 10:
                break
            file = await download_file(url)
            buffered_file = BufferedInputFile(
                BytesIO(file['file']).getvalue(),
                f'{file['name']}.{file['ext']}'
            )
            if file['ext'] in settings.attachment.image_extensions:
                media.append(InputMediaPhoto(media=buffered_file))
            elif file['ext'] in settings.attachment.video_extensions:
                media.append(InputMediaVideo(media=buffered_file))
        message.answer_media_group(media, caption=msg.text)
