from __future__ import annotations

import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiohttp import ClientTimeout

from config import BOT_TOKEN, DB_PATH, LOG_LEVEL
from db import Database
from handlers import common, menu, onboarding


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    )


async def main() -> None:
    setup_logging()

    if not BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN is empty. Fill .env before запуск.')

    db = Database(DB_PATH)
    db.init()

    session = AiohttpSession(timeout=ClientTimeout(total=300))  # 5 минут таймаут для больших файлов
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
    dp = Dispatcher()

    onboarding.set_db(db)
    menu.set_dependencies(db, bot)

    dp.include_router(onboarding.router)
    dp.include_router(menu.router)
    dp.include_router(common.router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
