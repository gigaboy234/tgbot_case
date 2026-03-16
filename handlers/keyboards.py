from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from config import COMMUNITY_LINKS, USEFUL_LINKS
from texts import (
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
    CONTACT_BUTTON_TEXT,
    CONTINUE_BUTTON_TEXT,
)


def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=CONTACT_BUTTON_TEXT, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def continue_keyboard(callback_data: str = 'continue') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=CONTINUE_BUTTON_TEXT, callback_data=callback_data)]])


def final_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ASK_QUESTION)],
            [KeyboardButton(text=BTN_REPORT_OR_ASK)],
            [KeyboardButton(text=BTN_USEFUL_LINKS)],
            [KeyboardButton(text=BTN_REPORT_BUG)],
        ],
        resize_keyboard=True,
    )


def request_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_TELL_SOMETHING)],
            [KeyboardButton(text=BTN_MEETING)],
            [KeyboardButton(text=BTN_HR_QUESTION)],
            [KeyboardButton(text=BTN_CANCEL_TO_MENU)],
        ],
        resize_keyboard=True,
    )


def useful_links_keyboard() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=text, url=url)] for text, url in USEFUL_LINKS.items()]
    rows.append([InlineKeyboardButton(text=BACK_TO_MENU_TEXT, callback_data='back_to_menu')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def communities_keyboard() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text=item.text, url=item.url)] for item in COMMUNITY_LINKS]
    rows.append([InlineKeyboardButton(text=CONTINUE_BUTTON_TEXT, callback_data='continue_after_communities')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BACK_TO_MENU_TEXT)],
            [KeyboardButton(text=BTN_MAIN_MENU)],
        ],
        resize_keyboard=True,
    )


def hr_escalation_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_YES_SEND)],
            [KeyboardButton(text=BTN_NO_BACK)],
        ],
        resize_keyboard=True,
    )
