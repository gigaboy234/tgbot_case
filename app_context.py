from __future__ import annotations

from db import Database


db: Database | None = None
service_chat_id: int = 0
request_types: dict[int, str] = {}
