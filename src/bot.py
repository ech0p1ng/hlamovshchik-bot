import logging
import asyncio
from aiogram import Bot, Dispatcher

import config
from menu import router as menu_router
from chat import router as chat_router


routers = [
    menu_router,
    chat_router,
]

if not config.BOT_TOKEN:
    print("Не указан BOT_TOKEN")
    exit()

bot = Bot(token=config.BOT_TOKEN)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(*routers)
    await dp.start_polling(bot)
