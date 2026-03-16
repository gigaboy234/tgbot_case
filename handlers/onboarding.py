from __future__ import annotations

import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import ABOUT_COMPANY_PDF_PATH, DIRECTOR_IMAGE_PATH, PRESENTATION_FILES
from db import Database
from handlers.keyboards import communities_keyboard, contact_keyboard, continue_keyboard, final_menu_keyboard
from states import UserState
from texts import (
    COMMUNITIES_TEXT,
    CONTACT_SUCCESS_TEMPLATE,
    DIRECTOR_CAPTION,
    FINAL_MENU_TEXT,
    WHO_WE_ARE_TEXT,
    WELCOME_TEXT,
    PRESENTATION_BLOCKS,
)

router = Router()
logger = logging.getLogger(__name__)

_db: Database | None = None


def set_db(db: Database) -> None:
    global _db
    _db = db


def get_db() -> Database:
    if _db is None:
        raise RuntimeError('Database is not initialized')
    return _db


def _display_name(message: Message) -> str:
    if message.contact and message.contact.first_name:
        return message.contact.first_name
    if message.from_user and message.from_user.first_name:
        return message.from_user.first_name
    return 'коллега'


async def _send_file_if_exists(message: Message, file_path: Path, caption: str | None = None) -> None:
    logger.info(f"Attempting to send file: {file_path}")
    logger.info(f"File exists: {file_path.exists()}, is_file: {file_path.is_file() if file_path.exists() else 'N/A'}")
    if file_path.exists():
        logger.info(f"File size: {file_path.stat().st_size} bytes")
    
    if file_path.exists() and file_path.is_file() and file_path.stat().st_size > 0:
        try:
            if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
                await message.answer_photo(photo=FSInputFile(file_path), caption=caption)
            else:
                await message.answer_document(document=FSInputFile(file_path), caption=caption)
            logger.info(f"File sent successfully: {file_path}")
        except Exception as e:
            logger.error(f"Failed to send file {file_path}: {e}")
            if caption:
                await message.answer(caption)
    elif caption:
        logger.warning(f"File not found or empty, sending caption only: {file_path}")
        await message.answer(caption)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    db = get_db()
    user = db.get_or_create_user(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    if user['phone']:
        db.clear_temp_request_type(message.from_user.id)
        db.clear_temp_kb_question(message.from_user.id)
        db.update_user_state(message.from_user.id, UserState.AFTER_CONTACT)
        await message.answer(f'С возвращением, {message.from_user.first_name or "коллега"}! Начинаем знакомство заново.')
        await _send_file_if_exists(message, DIRECTOR_IMAGE_PATH, DIRECTOR_CAPTION)
        await message.answer('Готов перейти к знакомству с компанией?', reply_markup=continue_keyboard('to_who_we_are'))
        return

    db.update_user_state(message.from_user.id, UserState.WAITING_FOR_CONTACT)
    await message.answer(WELCOME_TEXT, reply_markup=contact_keyboard())


@router.message(F.contact)
async def contact_handler(message: Message) -> None:
    db = get_db()
    contact = message.contact
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer('Пожалуйста, отправь свой собственный контакт через кнопку ниже.', reply_markup=contact_keyboard())
        return

    full_name = ' '.join(filter(None, [contact.first_name, contact.last_name])) or message.from_user.full_name
    db.update_user_contact(
        telegram_user_id=message.from_user.id,
        full_name=full_name,
        username=message.from_user.username,
        phone=contact.phone_number,
    )
    db.update_user_state(message.from_user.id, UserState.AFTER_CONTACT)

    await message.answer(CONTACT_SUCCESS_TEMPLATE.format(name=_display_name(message)))
    await _send_file_if_exists(message, DIRECTOR_IMAGE_PATH, DIRECTOR_CAPTION)
    await message.answer('Готов перейти к знакомству с компанией?', reply_markup=continue_keyboard('to_who_we_are'))


@router.callback_query(F.data == 'to_who_we_are')
async def to_who_we_are(callback: CallbackQuery) -> None:
    db = get_db()
    db.update_user_state(callback.from_user.id, UserState.WHO_WE_ARE)
    await callback.message.answer(WHO_WE_ARE_TEXT)
    await _send_file_if_exists(callback.message, ABOUT_COMPANY_PDF_PATH, 'PDF о компании')
    await callback.message.answer('Когда будешь готов, перейдём к блокам презентации.', reply_markup=continue_keyboard('presentation_1'))
    await callback.answer()


@router.callback_query(F.data.startswith('presentation_'))
async def presentation_handler(callback: CallbackQuery) -> None:
    db = get_db()
    block_number = int(callback.data.split('_')[1])
    block = PRESENTATION_BLOCKS[block_number]
    state = UserState[f'PRESENTATION_BLOCK_{block_number}']
    db.update_user_state(callback.from_user.id, state)

    await callback.message.answer(f"<b>{block['title']}</b>\n\n{block['text']}")
    await _send_file_if_exists(callback.message, PRESENTATION_FILES[block_number], f"Материал блока: {block['title']}")

    if block_number < 6:
        await callback.message.answer('Перейти к следующему блоку?', reply_markup=continue_keyboard(f'presentation_{block_number + 1}'))
    else:
        db.update_user_state(callback.from_user.id, UserState.COMMUNITIES)
        await callback.message.answer(COMMUNITIES_TEXT, reply_markup=communities_keyboard())
    await callback.answer()


@router.callback_query(F.data == 'continue_after_communities')
async def continue_after_communities(callback: CallbackQuery) -> None:
    db = get_db()
    db.update_user_state(callback.from_user.id, UserState.FINAL_MENU)
    await callback.message.answer(FINAL_MENU_TEXT, reply_markup=final_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: CallbackQuery) -> None:
    db = get_db()
    db.update_user_state(callback.from_user.id, UserState.FINAL_MENU)
    await callback.message.answer(FINAL_MENU_TEXT, reply_markup=final_menu_keyboard())
    await callback.answer()
