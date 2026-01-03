from functools import partial
from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from tg.parser import parse_messages_all
from message.services.service import MessageService

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")


@router.message(Command('parse'))
async def update_messages_base(message: types.Message) -> None:
    await message.answer('Ответ займет продолжительное время...')
    try:
        messages = await parse_messages_all()
    except Exception as e:
        await message.answer(f'Произошла ошибка: {str(e)}')
    else:
        for m in messages:
            # TODO сделать добавление сообщений в бд
            ...
