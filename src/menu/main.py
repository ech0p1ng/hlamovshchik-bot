from aiogram.filters import Command, CommandStart
from aiogram import types, F
from menu import router


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")
