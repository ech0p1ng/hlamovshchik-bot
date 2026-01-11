from functools import partial
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from dependencies import get_message_service
from db.database import get_db

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")


@router.message(Command("parse"))
async def update_messages_base(message: types.Message):
    async for db in get_db():
        message_service = await get_message_service(db)
        await message_service.update_all()
