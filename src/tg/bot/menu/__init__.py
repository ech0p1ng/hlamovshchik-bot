from functools import partial
from io import BytesIO
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaAudio
from typing import Any

from async_requests import download_file
from dependencies import get_message_service, get_minio_service, get_user_service, get_permission_service
from db.database import get_db
from config import get_settings
from user.models.model import UserModel
from user.schemas.schema import UserSimpleSchema
from role.models.model import RoleModel


router = Router()

FORBIDDEN_MSG = f'Доступ запрещен'


async def get_user(id: int, username: str | None) -> UserModel:
    '''
    Получить пользователя по его id и username

    Raises:
        RuntimeError: get_db() did not yield a session

    Returns:
        UserModel: SQLAlchemy модель пользователя
    '''
    filter = {'id': id}
    user: UserModel | None = None
    async for db in get_db():
        user_service = await get_user_service(db)
        if not await user_service.exists(filter, raise_exc=False):
            await user_service.create(UserModel.from_schema(
                UserSimpleSchema(id=id, user_name=username, role_id=2)
            ))
        user = await user_service.get(filter, [UserModel.role])
    if not user:
        raise RuntimeError("Пользователь не был создан")
    return user


async def _check_permission(command: str, user: UserModel) -> bool:
    '''
    Проверка доступа пользователя к команде бота

    Args:
        command (str): Команда бота
        user (UserModel): SQLAlchemy модель пользователя

    Returns:
        bool: `True` - доступ разрешен, `False` - доступ запрещен
    '''
    permitted = False
    async for db in get_db():
        permission_service = await get_permission_service(db)
        permitted = await permission_service.check_permission(
            command, user, raise_exc=False
        )
    return permitted


async def check_permission(command: str, message: types.Message) -> tuple[bool, str]:
    # ### ПРОВЕРКА ДОСТУПА ### #
    error_msg = FORBIDDEN_MSG
    if not message.from_user:
        error_msg = f'{FORBIDDEN_MSG}\n\nЯ не отвечаю не пересланные от каналов или ботов сообщения'
        return (False, error_msg)
    user = await get_user(message.from_user.id, message.from_user.username)
    permitted = await _check_permission(command, user)
    return (permitted, '' if permitted else FORBIDDEN_MSG)
    # ######################## #


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    permitted, msg = await check_permission('start', message)
    if not permitted:
        await message.answer(msg)
        return

    user = await get_user(message.from_user.id, message.from_user.username)  # type: ignore
    await message.answer(
        f"Привет, {user.user_name}! Я - Хламовщик, ищу картинки в Хламе по тексту в посте"
    )


@router.message(Command("parse"))
async def update_messages_base(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, msg = await check_permission('parse', message)
    if not permitted:
        await message.answer(msg)
        return
    # ######################## #

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
async def find_message(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, msg = await check_permission('find', message)
    if not permitted:
        await message.answer(msg)
        return
    # ######################## #

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
