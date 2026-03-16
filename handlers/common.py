from __future__ import annotations

import logging

from aiogram import Router
from aiogram.types import Message

from texts import UNEXPECTED_TEXT

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def fallback_handler(message: Message) -> None:
    await message.answer(UNEXPECTED_TEXT)
