import tg.bot
import asyncio
# from fill_db import fill_db


async def main() -> None:
    # await fill_db()
    await tg.bot.main()

if __name__ == '__main__':
    asyncio.run(main())
