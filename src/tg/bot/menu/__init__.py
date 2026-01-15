from functools import partial
from io import BytesIO
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
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
    get_user_service,
    get_permission_service,
    get_attachment_service,
    get_media_service,
)
from db.database import get_db
from config import get_settings
from user.models.model import UserModel
from user.schemas.schema import UserSimpleSchema
from role.models.model import RoleModel

router = Router()


@router.message(CommandStart())
async def start(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    if not message.from_user:
        return

    permitted = False
    answer = ''
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
            return

    # ######################## #
        await message.answer(
            f"Привет, {user.user_name}! Я - Хламовщик, ищу картинки в Хламе по тексту в посте"
        )


@router.message(Command("parse"))
async def parse(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    if not message.from_user:
        return

    permitted = False
    answer = ''
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
            return

    # ######################## #
        media_service = await get_media_service(db)
        async for msg in media_service.update_messages_base():
            await message.answer(msg)
    # ######################## #


@router.message(Command("find"))
async def find(message: types.Message) -> None:
    # ### ПРОВЕРКА ДОСТУПА ### #
    if not message.from_user:
        return

    permitted = False
    answer = ''
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
            return

    # ######################## #
        media_service = await get_media_service(db)
        error_msg = "Пожалуйста, укажите текст для поиска."
        if not message.text:
            await message.reply(error_msg)
            return

        query_text = message.text[len("/find "):].strip()

        if not query_text:
            await message.reply(error_msg)
            return

        async for media in media_service.inchat_media(query_text):
            await message.answer_media_group(media)
