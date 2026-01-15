from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from dependencies import (
    get_user_service,
    get_permission_service,
    get_media_service,
)
from db.database import get_db
from user.models.model import UserModel

router = Router()


async def check_permission(message: types.Message) -> tuple[bool, UserModel | None]:
    '''
    Проверка доступа пользователя, отправившего сообщение

    Args:
        message (types.Message): Сообщение, отправленное пользователем

    Returns:
        tuple[bool,UserModel|None]: `(permission, user)`. \
            `permission` - предоставить доступ, \
                `user` - SQLAlchemy модель пользователя
        ```
    '''
    permitted = False
    answer = ''
    user: UserModel | None = None

    if not message.from_user:
        return permitted, None

    async for db in get_db():
        user_service = await get_user_service(db)
        user = await user_service.get_by_id_and_name(
            message.from_user.id,
            message.from_user.username,
        )
        permission_service = await get_permission_service(db)
        permitted, answer = await permission_service.check_permission('find', user)
        if not permitted:
            await message.answer(answer)

    return permitted, user


@router.message(CommandStart())
async def start(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, user = await check_permission(message)
    if not permitted or not user:
        return
    # ######################## #

    await message.answer(
        f"Привет, {user.user_name}! Я - Хламовщик, ищу картинки в Хламе по тексту в посте"
    )


@router.message(Command("parse"))
async def parse(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, user = await check_permission(message)
    if not permitted or not user:
        return
    # ######################## #

    async for db in get_db():
        media_service = await get_media_service(db)
        async for msg in media_service.update_messages_base():
            await message.answer(msg)


@router.message(Command("find"))
async def find(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, user = await check_permission(message)
    if not permitted or not user:
        return
    # ######################## #

    async for db in get_db():
        error_msg = "Пожалуйста, укажите текст для поиска."
        if not message.text:
            await message.reply(error_msg)
            return

        query_text = message.text[len("/find "):].strip()

        if not query_text:
            await message.reply(error_msg)
            return

        media_service = await get_media_service(db)

        async for media in media_service.inchat_media(query_text):
            await message.answer_media_group(media)
