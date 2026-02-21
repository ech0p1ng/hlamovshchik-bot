from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    InputMediaAudio,
    InlineQueryResultPhoto,
    InlineQueryResultVideo,
    InlineQueryResultDocument,
    InlineQueryResultAudio,
)

from bot_request.schemas.schema import BotRequestCreateSchema
from bot_request.models.model import BotRequestModel
from dependencies import (
    get_user_service,
    get_media_service,
    get_bot_request_service
)
from db.database import get_db
from user.models.model import UserModel
from exceptions.exception import NotFoundError

router = Router()


async def send_single_media(
    message: types.Message,
    media: InputMediaPhoto | InputMediaVideo | InputMediaDocument | InputMediaAudio
) -> None:
    if isinstance(media, InputMediaPhoto):
        await message.answer_photo(media.media, caption=media.caption)

    elif isinstance(media, InputMediaVideo):
        await message.answer_video(media.media, caption=media.caption)

    elif isinstance(media, InputMediaDocument):
        await message.answer_document(media.media, caption=media.caption)

    elif isinstance(media, InputMediaAudio):
        await message.answer_audio(media.media, caption=media.caption)

    else:
        raise ValueError("Unsupported media type")


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
        async for msg in media_service.update_messages_base(show_msg=True):
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

        bot_request_service = await get_bot_request_service(db)
        await bot_request_service.create(
            BotRequestModel.from_schema(BotRequestCreateSchema(
                user_id=user.id,
                text=query_text,
                request_type='chat'
            ))
        )

        if not query_text:
            await message.reply(error_msg)
            return

        media_service = await get_media_service(db)

        try:
            media_list = await media_service.inchat_media(query_text)

            if not media_list:
                raise NotFoundError(f'Ничего не найдено с текстом "{query_text}"')

            if len(media_list) == 1:
                await send_single_media(message, media_list[0])
            elif len(media_list) > 10:
                for i in range(0, len(media_list), 10):
                    chunk = media_list[i:i + 10]
                    await message.answer_media_group(chunk)
            else:
                await message.answer_media_group(media_list)

        except NotFoundError as e:
            await message.answer(str(e))


@router.inline_query()
async def inline_msg(inline_query: types.InlineQuery) -> None:
    async def __empty_answer(cache_time: int):
        await inline_query.answer(
            results=[],
            cache_time=cache_time
        )

    # ### ПРОВЕРКА ДОСТУПА ### #
    permitted, user = await check_permission(inline_query)
    if not permitted or not user:
        return
    # ######################## #

    query_text = inline_query.query.strip().lower()

    limit = 50
    offset = int(inline_query.offset or 0)

    results = []
    cache_time = 1
    if not query_text or len(query_text) <= 1:
        await __empty_answer(cache_time)
        return

    async for db in get_db():
        media_service = await get_media_service(db)

        bot_request_service = await get_bot_request_service(db)
        await bot_request_service.create(
            BotRequestModel.from_schema(BotRequestCreateSchema(
                user_id=user.id,
                text=query_text,
                request_type='inline',
            ))
        )

        try:
            media_list = await media_service.inline_media(query_text)
        except NotFoundError:
            await __empty_answer(cache_time)
            return

        for inline_media in media_list:
            results.append(inline_media)

    if not results:
        await __empty_answer(cache_time)
        return

    next_offset = str(offset + limit) if len(results) > offset + limit else None

    if results:
        await inline_query.answer(
            results=results[offset:offset + limit],  # type: ignore
            next_offset=next_offset,
            cache_time=cache_time
        )
