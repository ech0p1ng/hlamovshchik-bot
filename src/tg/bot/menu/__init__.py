from aiogram import types, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
import json
from tg.parser import parse_messages
import asyncio
import random
from logger import logger

router = Router()


@router.message(CommandStart())
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Я асинхронный бот на aiogram 🚀")


@router.message(Command('parse'))
async def update_messages_base(message: types.Message) -> None:
    await message.answer('Ответ займет продолжительное время...')
    parsed = await parse_messages(before=0)
    if parsed is not None:
        last_msg_id = parsed[-1]['id'] + 10  # 10 с запасом на изображения, которые считаются за отдельные сообщения
        msg_id = 0
        count = 1

        while msg_id < last_msg_id:
            parsed = await parse_messages(after=count)
            if parsed is not None:
                count += len(parsed)
                for m in parsed:
                    logger.info(json.dumps(m, ensure_ascii=False, indent=2))
                    await message.answer('\n'.join(m['image_urls']))
            await asyncio.sleep(random.randint(2, 5))
    else:
        await message.answer('Не удалось спарсить сообщения')
