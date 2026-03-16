from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from states import UserState


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id INTEGER NOT NULL UNIQUE,
                    full_name TEXT,
                    username TEXT,
                    phone TEXT,
                    created_at TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    current_request_type TEXT,
                    temp_request_type TEXT
                );

                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS employee_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    category TEXT,
                    answer_text TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                '''
            )
            self._ensure_column(conn, 'users', 'temp_request_type', 'TEXT')

    @staticmethod
    def _ensure_column(conn: sqlite3.Connection, table: str, column: str, column_type: str) -> None:
        columns = {row['name'] for row in conn.execute(f'PRAGMA table_info({table})').fetchall()}
        if column not in columns:
            conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {column_type}')

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def get_or_create_user(self, telegram_user_id: int, username: str | None, full_name: str | None) -> sqlite3.Row:
        with self.connect() as conn:
            row = conn.execute('SELECT * FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()
            if row:
                return row
            created_at = self._now()
            conn.execute(
                '''
                INSERT INTO users (telegram_user_id, full_name, username, phone, created_at, current_state, current_request_type, temp_request_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    telegram_user_id,
                    full_name,
                    username,
                    None,
                    created_at,
                    UserState.WAITING_FOR_CONTACT.value,
                    None,
                    None,
                ),
            )
            return conn.execute('SELECT * FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()

    def get_user_by_telegram_id(self, telegram_user_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute('SELECT * FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()

    def update_user_contact(self, telegram_user_id: int, full_name: str | None, username: str | None, phone: str) -> None:
        with self.connect() as conn:
            conn.execute(
                '''
                UPDATE users
                SET full_name = ?, username = ?, phone = ?, current_state = ?, current_request_type = NULL, temp_request_type = NULL
                WHERE telegram_user_id = ?
                ''',
                (full_name, username, phone, UserState.AFTER_CONTACT.value, telegram_user_id),
            )

    def update_user_state(self, telegram_user_id: int, state: UserState, request_type: str | None = None) -> None:
        with self.connect() as conn:
            if request_type is None:
                conn.execute('UPDATE users SET current_state = ? WHERE telegram_user_id = ?', (state.value, telegram_user_id))
            else:
                conn.execute(
                    'UPDATE users SET current_state = ?, current_request_type = ? WHERE telegram_user_id = ?',
                    (state.value, request_type, telegram_user_id),
                )

    def save_request(self, telegram_user_id: int, request_type: str, text: str) -> None:
        with self.connect() as conn:
            user = conn.execute('SELECT id FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()
            if not user:
                raise ValueError('User not found')
            conn.execute(
                'INSERT INTO requests (user_id, type, text, created_at) VALUES (?, ?, ?, ?)',
                (user['id'], request_type, text, self._now()),
            )

    def save_error(self, telegram_user_id: int, text: str) -> None:
        with self.connect() as conn:
            user = conn.execute('SELECT id FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()
            if not user:
                raise ValueError('User not found')
            conn.execute(
                'INSERT INTO errors (user_id, text, created_at) VALUES (?, ?, ?)',
                (user['id'], text, self._now()),
            )

    def save_employee_question(
        self,
        telegram_user_id: int,
        question_text: str,
        category: str | None,
        answer_text: str | None,
        status: str,
    ) -> None:
        with self.connect() as conn:
            user = conn.execute('SELECT id FROM users WHERE telegram_user_id = ?', (telegram_user_id,)).fetchone()
            if not user:
                raise ValueError('User not found')
            conn.execute(
                '''
                INSERT INTO employee_questions (user_id, question_text, category, answer_text, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (user['id'], question_text, category, answer_text, status, self._now()),
            )

    def user_has_contact(self, telegram_user_id: int) -> bool:
        row = self.get_user_by_telegram_id(telegram_user_id)
        return bool(row and row['phone'])

    def get_user_state(self, telegram_user_id: int) -> UserState | None:
        row = self.get_user_by_telegram_id(telegram_user_id)
        if not row:
            return None
        return UserState(row['current_state'])

    def get_current_request_type(self, telegram_user_id: int) -> str | None:
        row = self.get_user_by_telegram_id(telegram_user_id)
        if not row:
            return None
        return row['current_request_type']

    def clear_temp_request_type(self, telegram_user_id: int) -> None:
        with self.connect() as conn:
            conn.execute('UPDATE users SET current_request_type = NULL WHERE telegram_user_id = ?', (telegram_user_id,))

    def save_temp_kb_question(self, telegram_user_id: int, question_text: str) -> None:
        with self.connect() as conn:
            conn.execute('UPDATE users SET temp_request_type = ? WHERE telegram_user_id = ?', (question_text, telegram_user_id))

    def get_temp_kb_question(self, telegram_user_id: int) -> str | None:
        row = self.get_user_by_telegram_id(telegram_user_id)
        if not row:
            return None
        return row['temp_request_type']

    def clear_temp_kb_question(self, telegram_user_id: int) -> None:
        with self.connect() as conn:
            conn.execute('UPDATE users SET temp_request_type = NULL WHERE telegram_user_id = ?', (telegram_user_id,))

    def to_dict(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return dict(row)
