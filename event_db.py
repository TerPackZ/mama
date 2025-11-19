import sqlite3
from typing import List, Tuple  # ← добавь, если ещё нет

EVENT_DB_PATH = "event_requests.db"


def get_conn():
    return sqlite3.connect(EVENT_DB_PATH)

def init_event_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS event_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            full_name TEXT NOT NULL,
            role TEXT,
            event_title TEXT NOT NULL,
            event_type TEXT,
            audience_type TEXT,
            event_date TEXT,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            expected_participants TEXT,
            multimedia_needs TEXT,
            needs_recording TEXT,
            needs_streaming TEXT,
            email TEXT,
            phone TEXT,
            comment TEXT,
            status TEXT DEFAULT 'ожидает'
        )
        """
    )
    conn.commit()
    conn.close()


def insert_event_request(
    full_name: str,
    role: str,
    event_title: str,
    event_type: str,
    audience_type: str,
    event_date: str,
    start_time: str,
    end_time: str,
    location: str,
    expected_participants: str,
    multimedia_needs: str,
    needs_recording: str,
    needs_streaming: str,
    email: str,
    phone: str,
    comment: str,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO event_requests (
            full_name, role, event_title, event_type,
            audience_type, event_date, start_time, end_time,
            location, expected_participants,
            multimedia_needs, needs_recording, needs_streaming,
            email, phone, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            role,
            event_title,
            event_type,
            audience_type,
            event_date,
            start_time,
            end_time,
            location,
            expected_participants,
            multimedia_needs,
            needs_recording,
            needs_streaming,
            email,
            phone,
            comment,
        ),
    )
    conn.commit()
    conn.close()

def get_all_event_requests() -> List[Tuple]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at,
               full_name, role, event_title, event_type,
               audience_type, event_date, start_time, end_time,
               location, expected_participants,
               multimedia_needs, needs_recording, needs_streaming,
               email, phone, comment
        FROM event_requests
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows