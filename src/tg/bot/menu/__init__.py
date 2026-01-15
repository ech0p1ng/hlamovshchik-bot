from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from dependencies import (
    get_user_service,
    get_media_service,
)
from db.database import get_db
from user.models.model import UserModel
from exceptions.exception import NotFoundError

router = Router()


async def check_permission(message: types.Message | types.InlineQuery) -> tuple[bool, UserModel | None]:
    '''
    Проверка доступа пользователя, отправившего сообщение

    Args:
        message (types.Message | types.InlineQuery): Сообщение, отправленное пользователем

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
        permitted, answer = await user_service.check_permission(
            'find',
            message.from_user.id,
            message.from_user.username,
        )
        if not permitted and type(message) is types.Message:
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

        query_text = message.text[len("/find "):].strip().lower()

        if not query_text:
            await message.reply(error_msg)
            return

        media_service = await get_media_service(db)

        try:
            async for media in media_service.inchat_media(query_text):
                await message.answer_media_group(media)
        except NotFoundError as e:
            await message.answer(str(e))


@router.inline_query()
async def inline_msg(inline_query: types.InlineQuery) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, user = await check_permission(inline_query)
    if not permitted or not user:
        return
    # ######################## #
    query_text = inline_query.query.strip().lower()
    try:
        async for db in get_db():
            media_service = await get_media_service(db)
            async for media in media_service.inline_media(query_text):
                await inline_query.answer(media)  # type: ignore
    except Exception:
        pass
