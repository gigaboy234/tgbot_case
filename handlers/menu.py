from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import Message

from config import ADMIN_CHAT_ID
from db import Database
from handlers.keyboards import (
    back_to_menu_keyboard,
    final_menu_keyboard,
    hr_escalation_keyboard,
    request_type_keyboard,
    useful_links_keyboard,
)
from knowledge_base import CATEGORY_LABELS, classify_question, find_best_entry, should_escalate
from states import UserState
from texts import (
    ASK_QUESTION_TEXT,
    BACK_TO_MENU_TEXT,
    BTN_ASK_QUESTION,
    BTN_CANCEL_TO_MENU,
    BTN_HR_QUESTION,
    BTN_MAIN_MENU,
    BTN_MEETING,
    BTN_NO_BACK,
    BTN_REPORT_BUG,
    BTN_REPORT_OR_ASK,
    BTN_TELL_SOMETHING,
    BTN_USEFUL_LINKS,
    BTN_YES_SEND,
    CLARIFY_PROMPT_PREFIX,
    ERROR_PROMPT,
    ERROR_SAVED_TEXT,
    FINAL_MENU_TEXT,
    HR_ESCALATION_DONE_TEXT,
    HR_ESCALATION_TEXT,
    KB_ANSWER_FOOTER,
    REQUEST_SAVED_TEXT,
    REQUEST_TEXT_PROMPT,
    REQUEST_TYPE_PROMPT,
    UNKNOWN_QUESTION_TEXT,
    USEFUL_LINKS_TEXT,
)

router = Router()
logger = logging.getLogger(__name__)

_db: Database | None = None
_bot = None


def set_dependencies(db: Database, bot) -> None:
    global _db, _bot
    _db = db
    _bot = bot


def get_db() -> Database:
    if _db is None:
        raise RuntimeError('Database is not initialized')
    return _db


async def _notify_admin(text: str) -> None:
    if ADMIN_CHAT_ID and _bot is not None:
        await _bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)


@router.message(F.text == BTN_ASK_QUESTION)
async def ask_question_entry(message: Message) -> None:
    db = get_db()
    db.update_user_state(message.from_user.id, UserState.WAITING_FOR_KB_QUESTION)
    await message.answer(ASK_QUESTION_TEXT, reply_markup=back_to_menu_keyboard())


@router.message(F.text == BTN_REPORT_OR_ASK)
async def report_or_ask(message: Message) -> None:
    db = get_db()
    db.update_user_state(message.from_user.id, UserState.ASK_REQUEST_TYPE)
    await message.answer(REQUEST_TYPE_PROMPT, reply_markup=request_type_keyboard())


@router.message(F.text.in_({BTN_TELL_SOMETHING, BTN_MEETING, BTN_HR_QUESTION}))
async def choose_request_type(message: Message) -> None:
    db = get_db()
    mapping = {
        BTN_TELL_SOMETHING: 'рассказать',
        BTN_MEETING: 'встреча',
        BTN_HR_QUESTION: 'HR',
    }
    request_type = mapping[message.text]
    db.update_user_state(message.from_user.id, UserState.WAITING_FOR_REQUEST_TEXT, request_type=request_type)
    await message.answer(REQUEST_TEXT_PROMPT)


@router.message(F.text.in_({BTN_CANCEL_TO_MENU, BACK_TO_MENU_TEXT, BTN_MAIN_MENU, BTN_NO_BACK}))
async def cancel_to_menu(message: Message) -> None:
    db = get_db()
    db.clear_temp_request_type(message.from_user.id)
    db.clear_temp_kb_question(message.from_user.id)
    db.update_user_state(message.from_user.id, UserState.FINAL_MENU)
    await message.answer(FINAL_MENU_TEXT, reply_markup=final_menu_keyboard())


@router.message(F.text == BTN_USEFUL_LINKS)
async def useful_links(message: Message) -> None:
    db = get_db()
    db.update_user_state(message.from_user.id, UserState.USEFUL_LINKS)
    await message.answer(USEFUL_LINKS_TEXT, reply_markup=useful_links_keyboard())


@router.message(F.text == BTN_REPORT_BUG)
async def report_bug(message: Message) -> None:
    db = get_db()
    db.update_user_state(message.from_user.id, UserState.WAITING_FOR_ERROR_TEXT)
    await message.answer(ERROR_PROMPT)


@router.message()
async def catch_text_flows(message: Message) -> None:
    db = get_db()
    state = db.get_user_state(message.from_user.id)

    if state == UserState.WAITING_FOR_KB_QUESTION:
        question = (message.text or '').strip()
        if not question:
            await message.answer('Напиши вопрос текстом одним сообщением.')
            return
        entry = find_best_entry(question)
        category = classify_question(question)
        if not entry:
            db.save_employee_question(message.from_user.id, question, category, None, 'unknown')
            await message.answer(UNKNOWN_QUESTION_TEXT, reply_markup=back_to_menu_keyboard())
            return
        if entry.clarify:
            db.save_temp_kb_question(message.from_user.id, question)
            db.update_user_state(message.from_user.id, UserState.WAITING_FOR_KB_CLARIFICATION)
            db.save_employee_question(message.from_user.id, question, entry.category, None, 'clarification_requested')
            await message.answer(f'{CLARIFY_PROMPT_PREFIX}{entry.clarify}', reply_markup=back_to_menu_keyboard())
            return
        if should_escalate(question, entry):
            db.save_temp_kb_question(message.from_user.id, question)
            db.update_user_state(message.from_user.id, UserState.WAITING_FOR_HR_ESCALATION_CONFIRM)
            db.save_employee_question(message.from_user.id, question, entry.category, entry.answer, 'escalation_offered')
            await message.answer(HR_ESCALATION_TEXT, reply_markup=hr_escalation_keyboard())
            return
        answer = f'Категория: {CATEGORY_LABELS.get(entry.category, entry.category)}\n\n{entry.answer}{KB_ANSWER_FOOTER}'
        db.save_employee_question(message.from_user.id, question, entry.category, entry.answer, 'answered')
        await message.answer(answer, reply_markup=back_to_menu_keyboard())
        return

    if state == UserState.WAITING_FOR_KB_CLARIFICATION:
        original_question = db.get_temp_kb_question(message.from_user.id) or ''
        clarification = (message.text or '').strip()
        full_question = f'{original_question}. Уточнение: {clarification}'.strip()
        entry = find_best_entry(full_question)
        category = classify_question(full_question)
        if not entry:
            db.save_employee_question(message.from_user.id, full_question, category, None, 'unknown_after_clarification')
            db.update_user_state(message.from_user.id, UserState.WAITING_FOR_HR_ESCALATION_CONFIRM)
            db.save_temp_kb_question(message.from_user.id, full_question)
            await message.answer(
                'Спасибо, теперь вопрос понятнее. Но для точного ответа лучше подключить HR или администратора процесса.',
                reply_markup=hr_escalation_keyboard(),
            )
            return
        if should_escalate(full_question, entry):
            db.save_temp_kb_question(message.from_user.id, full_question)
            db.update_user_state(message.from_user.id, UserState.WAITING_FOR_HR_ESCALATION_CONFIRM)
            db.save_employee_question(
                message.from_user.id,
                full_question,
                entry.category,
                entry.answer,
                'escalation_offered_after_clarification',
            )
            await message.answer(HR_ESCALATION_TEXT, reply_markup=hr_escalation_keyboard())
            return
        db.clear_temp_kb_question(message.from_user.id)
        db.update_user_state(message.from_user.id, UserState.WAITING_FOR_KB_QUESTION)
        answer = f'Категория: {CATEGORY_LABELS.get(entry.category, entry.category)}\n\n{entry.answer}{KB_ANSWER_FOOTER}'
        db.save_employee_question(message.from_user.id, full_question, entry.category, entry.answer, 'answered_after_clarification')
        await message.answer(answer, reply_markup=back_to_menu_keyboard())
        return

    if state == UserState.WAITING_FOR_HR_ESCALATION_CONFIRM:
        if message.text == BTN_YES_SEND:
            question = db.get_temp_kb_question(message.from_user.id) or 'Без текста'
            db.save_request(message.from_user.id, 'HR_ESCALATION', question)
            db.save_employee_question(message.from_user.id, question, 'hr', 'Передано в HR', 'escalated_to_hr')
            await _notify_admin(
                f'Эскалация в HR\n'
                f'User ID: {message.from_user.id}\n'
                f'Username: @{message.from_user.username if message.from_user.username else "-"}\n'
                f'Имя: {message.from_user.full_name}\n\n'
                f'Вопрос:\n{question}'
            )
            db.clear_temp_kb_question(message.from_user.id)
            db.update_user_state(message.from_user.id, UserState.FINAL_MENU)
            await message.answer(HR_ESCALATION_DONE_TEXT, reply_markup=final_menu_keyboard())
            return
        if message.text == BTN_NO_BACK:
            db.clear_temp_kb_question(message.from_user.id)
            db.update_user_state(message.from_user.id, UserState.FINAL_MENU)
            await message.answer('Хорошо, возвращаю в меню.', reply_markup=final_menu_keyboard())
            return
        await message.answer('Пожалуйста, выбери один из вариантов кнопками ниже.', reply_markup=hr_escalation_keyboard())
        return

    if state == UserState.WAITING_FOR_REQUEST_TEXT:
        request_type = db.get_current_request_type(message.from_user.id) or 'прочее'
        db.save_request(message.from_user.id, request_type, message.text or '')
        db.clear_temp_request_type(message.from_user.id)
        db.update_user_state(message.from_user.id, UserState.FINAL_MENU)
        await _notify_admin(
            f'Новое обращение\nТип: {request_type}\nUser ID: {message.from_user.id}\n'
            f'Username: @{message.from_user.username if message.from_user.username else "-"}\n\n{message.text}'
        )
        await message.answer(REQUEST_SAVED_TEXT, reply_markup=final_menu_keyboard())
        return

    if state == UserState.WAITING_FOR_ERROR_TEXT:
        db.save_error(message.from_user.id, message.text or '')
        db.update_user_state(message.from_user.id, UserState.FINAL_MENU)
        await _notify_admin(
            f'Новое сообщение об ошибке\nUser ID: {message.from_user.id}\n'
            f'Username: @{message.from_user.username if message.from_user.username else "-"}\n\n{message.text}'
        )
        await message.answer(ERROR_SAVED_TEXT, reply_markup=final_menu_keyboard())
        return

    await message.answer('Не совсем понял сообщение. Выбери действие через кнопки меню.', reply_markup=final_menu_keyboard())
