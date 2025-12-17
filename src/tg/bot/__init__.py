import logging
import asyncio
from aiogram import Bot, Dispatcher

from config import settings
from tg.bot.menu import router as menu_router
from tg.bot.chat import router as chat_router


routers = [
    menu_router,
    chat_router,
]

if not settings.telegram.bot_token:
    print("Не указан BOT_TOKEN")
    exit()

bot = Bot(token=settings.telegram.bot_token)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(*routers)
    await dp.start_polling(bot)
