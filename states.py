from __future__ import annotations

from enum import StrEnum


class UserState(StrEnum):
    NEW = 'new'
    WAITING_FOR_CONTACT = 'waiting_for_contact'
    AFTER_CONTACT = 'after_contact'
    WHO_WE_ARE = 'who_we_are'
    PRESENTATION_BLOCK_1 = 'presentation_block_1'
    PRESENTATION_BLOCK_2 = 'presentation_block_2'
    PRESENTATION_BLOCK_3 = 'presentation_block_3'
    PRESENTATION_BLOCK_4 = 'presentation_block_4'
    PRESENTATION_BLOCK_5 = 'presentation_block_5'
    PRESENTATION_BLOCK_6 = 'presentation_block_6'
    COMMUNITIES = 'communities'
    FINAL_MENU = 'final_menu'
    ASK_REQUEST_TYPE = 'ask_request_type'
    WAITING_FOR_REQUEST_TEXT = 'waiting_for_request_text'
    USEFUL_LINKS = 'useful_links'
    WAITING_FOR_ERROR_TEXT = 'waiting_for_error_text'
    WAITING_FOR_KB_QUESTION = 'waiting_for_kb_question'
    WAITING_FOR_KB_CLARIFICATION = 'waiting_for_kb_clarification'
    WAITING_FOR_HR_ESCALATION_CONFIRM = 'waiting_for_hr_escalation_confirm'


PRESENTATION_STATE_ORDER = [
    UserState.PRESENTATION_BLOCK_1,
    UserState.PRESENTATION_BLOCK_2,
    UserState.PRESENTATION_BLOCK_3,
    UserState.PRESENTATION_BLOCK_4,
    UserState.PRESENTATION_BLOCK_5,
    UserState.PRESENTATION_BLOCK_6,
]
