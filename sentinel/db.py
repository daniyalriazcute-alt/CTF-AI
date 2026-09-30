"""SQLite persistence for chat history and guardrail events."""

import os
import sqlite3
import json
from datetime import datetime
from typing import Any

DB_PATH = os.getenv("DB_PATH", "sentinel.db")


def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT,
                ended_at TEXT
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                role TEXT,
                content TEXT,
                tokens INTEGER DEFAULT 0,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS guardrail_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                layer TEXT,
                snippet TEXT,
                created_at TEXT
            );
            """
        )


def new_session() -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO sessions (started_at) VALUES (?)",
            (datetime.utcnow().isoformat(),),
        )
        return cur.lastrowid


def end_session(session_id: int) -> None:
    with _conn() as c:
        c.execute(
            "UPDATE sessions SET ended_at=? WHERE id=?",
            (datetime.utcnow().isoformat(), session_id),
        )


def save_message(session_id: int, role: str, content: str, tokens: int = 0) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (session_id, role, content, tokens, created_at) VALUES (?,?,?,?,?)",
            (session_id, role, content, tokens, datetime.utcnow().isoformat()),
        )


def log_guardrail(session_id: int, layer: str, snippet: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO guardrail_events (session_id, layer, snippet, created_at) VALUES (?,?,?,?)",
            (session_id, layer, snippet[:200], datetime.utcnow().isoformat()),
        )


def list_sessions() -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            "SELECT id, started_at, ended_at FROM sessions ORDER BY id DESC LIMIT 30"
        ).fetchall()
        return [dict(r) for r in rows]


def session_messages(session_id: int) -> list[dict[str, Any]]:
    with _conn() as c:
        rows = c.execute(
            "SELECT role, content, tokens, created_at FROM messages WHERE session_id=? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def clear_all() -> None:
    with _conn() as c:
        c.executescript(
            "DELETE FROM messages; DELETE FROM sessions; DELETE FROM guardrail_events;"
        )
