from functools import partial
from io import BytesIO
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio

from async_requests import download_file
from dependencies import get_message_service, get_minio_service, get_user_service
from db.database import get_db
from config import get_settings
from user.models.model import UserModel
from user.schemas.schema import UserSimpleSchema

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    if not message.from_user:
        return

    is_newbie = True
    user: UserModel | None = None
    id = message.from_user.id
    username = message.from_user.username
    filter = {'id': id}

    async for db in get_db():
        user_service = await get_user_service(db)
        if await user_service.exists(filter, raise_exc=False):
            user = await user_service.get(filter)
            is_newbie = False
        else:
            user = await user_service.create(UserModel.from_schema(
                UserSimpleSchema(id=id, user_name=username, role_id=2)
            ))

        if is_newbie:
            msg = f"Привет, {user.user_name}! Я - Хламовщик, ищу картинки в Хламе по тексту в посте"
        else:
            msg = f'С возвращением, {user.user_name}!'
        await message.answer(msg)


@router.message(Command("parse"))
async def update_messages_base(message: types.Message):
    await message.answer('Запуск парсинга...')
    show_msg = True
    async for db in get_db():
        message_service = await get_message_service(db)
        async for msg in message_service.upload_all():
            if show_msg:
                current = ', '.join([str(msg_id) for msg_id in msg['current']])
                last = msg['last']
                first = msg['first']
                total = msg['total']
                output = (f'Парсинг...\n\n'
                          f'ID первого: {first}\n'
                          f'ID последнего: {last}\n'
                          f'ID текущих: {current}\n'
                          f'Итого сообщений за этот момент: {total}')
                await message.answer(output)


@router.message(Command("find"))
async def find_message(message: types.Message):
    error_msg = "Пожалуйста, укажите текст для поиска."
    if not message.text:
        await message.reply(error_msg)
        return

    query_text = message.text[len("/find "):].strip()

    if not query_text:
        await message.reply(error_msg)
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
            file_data = await download_file(url)
            file: BytesIO = file_data['file']
            buffered_file = BufferedInputFile(
                file.getvalue(),
                f'{file_data['name']}.{file_data['ext']}'
            )
            if file_data['ext'] in settings.attachment.image_extensions:
                media.append(InputMediaPhoto(media=buffered_file))
            elif file_data['ext'] in settings.attachment.video_extensions:
                media.append(InputMediaVideo(media=buffered_file))
        await message.answer_media_group(media, caption=msg.text)
