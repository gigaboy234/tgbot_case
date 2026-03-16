from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / 'files'
IMAGES_DIR = FILES_DIR / 'images'
PDF_DIR = FILES_DIR / 'pdf'
PRESENTATIONS_DIR = FILES_DIR / 'presentations'
DB_PATH = BASE_DIR / 'bot.sqlite3'


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or value == '':
        return default
    return int(value)


@dataclass(frozen=True)
class CommunityLink:
    text: str
    url: str


BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_CHAT_ID = _env_int('ADMIN_CHAT_ID')

DIRECTOR_IMAGE_PATH = IMAGES_DIR / 'director.jpg'
ABOUT_COMPANY_PDF_PATH = PDF_DIR / 'about_company.pdf'

COMMUNITY_LINKS = [
    CommunityLink(text='Сообщество 1', url=os.getenv('COMMUNITY_URL_1', 'https://t.me/example_community_1')),
    CommunityLink(text='Сообщество 2', url=os.getenv('COMMUNITY_URL_2', 'https://t.me/example_community_2')),
]

USEFUL_LINKS = {
    'Корпоративный портал': os.getenv('USEFUL_LINK_PORTAL', 'https://example.com/portal'),
    'База знаний': os.getenv('USEFUL_LINK_KB', 'https://example.com/kb'),
    'HR-ресурсы': os.getenv('USEFUL_LINK_HR', 'https://example.com/hr'),
    'Заявки в IT': os.getenv('USEFUL_LINK_IT', 'https://example.com/it'),
}

PRESENTATION_FILES = {
    1: PRESENTATIONS_DIR / 'block_1_safety.pdf',
    2: PRESENTATIONS_DIR / 'block_2_communications.pdf',
    3: PRESENTATIONS_DIR / 'block_3_hr.pdf',
    4: PRESENTATIONS_DIR / 'block_4_useful_info.pdf',
    5: PRESENTATIONS_DIR / 'block_5_union.pdf',
    6: PRESENTATIONS_DIR / 'block_6_services.pdf',
}

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
