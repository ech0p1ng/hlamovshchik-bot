import logging
import asyncio
from aiogram import Bot, Dispatcher

from config import get_settings
from tg.bot.menu import router as menu_router
from tg.bot.chat import router as chat_router
from tg.bot.logs import setup_async_tg_logger

routers = [
    menu_router,
    chat_router,
]

if not get_settings().telegram.bot_token:
    print("Не указан BOT_TOKEN")
    exit()

bot = Bot(token=get_settings().telegram.bot_token)
tg_handler = setup_async_tg_logger(bot, get_settings().telegram.chat_id)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_routers(*routers)
    await dp.start_polling(bot)
