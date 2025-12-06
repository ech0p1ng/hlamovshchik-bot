import os
from config import init
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

init()

BOT_API_KEY = os.getenv('BOT_API_KEY')
CHANNEL_ID = os.getenv('CHANNEL_ID')


async def main():
    bot = Bot(token=BOT_API_KEY)  # type: ignore
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        await message.answer("Привет! Я асинхронный бот на aiogram 🚀")

    # Запуск опроса (polling)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
