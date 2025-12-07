from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
import config
import json
from parser import parse_messages

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")


@router.message(Command('parse'))
async def update_messages_base(message: types.Message) -> None:
    parsed = await parse_messages()
    data_json = json.dumps(parsed, ensure_ascii=False, indent=2)
    if parsed:
        await message.answer('Парсинг прошел успешно')
    else:
        await message.answer('Не удалось спарсить сообщения')
