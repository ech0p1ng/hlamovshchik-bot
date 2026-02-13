import asyncio
import logging
from typing import Optional
import contextlib

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter


class AsyncTelegramHandler(logging.Handler):
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        *,
        level=logging.INFO,
        queue_size: int = 1000,
        rate_limit: float = 0.5,  # секунд между сообщениями
    ):
        super().__init__(level)
        self.bot = bot
        self.chat_id = chat_id
        self.queue: asyncio.Queue[str] = asyncio.Queue(queue_size)
        self.rate_limit = rate_limit
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._worker())

    async def stop(self):
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass  # защита от переполнения

    async def _worker(self):
        while True:
            msg = await self.queue.get()
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=msg[:4096],
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                await asyncio.sleep(self.rate_limit)

            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)

            except Exception:
                pass


class TelegramFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level_icon = {
            "DEBUG": "🟦",
            "INFO": "🟩",
            "WARNING": "🟨",
            "ERROR": "🟥",
            "CRITICAL": "🔥",
        }.get(record.levelname, "⬜")

        return (
            f"{level_icon} <b>{record.levelname}</b>\n"
            f"{record.getMessage()}\n\n"
            f"<i>{record.filename}:{record.lineno}</i>\n"
            f"<code>{record.funcName}</code>"
        )


def setup_async_tg_logger(bot: Bot, chat_id: int) -> AsyncTelegramHandler:
    logger = logging.getLogger("tg_logger")
    logger.setLevel(logging.INFO)

    handler = AsyncTelegramHandler(bot, chat_id)
    handler.setFormatter(TelegramFormatter())

    logger.addHandler(handler)
    logger.propagate = False

    return handler
