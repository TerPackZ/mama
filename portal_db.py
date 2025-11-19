import sqlite3
from typing import List, Tuple, Optional

PORTAL_DB_PATH = "portal_requests.db"


def get_conn():
    return sqlite3.connect(PORTAL_DB_PATH)


def init_portal_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS portal_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            faculty TEXT,
            portal_section TEXT,
            issue_type TEXT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'new'
        )
        """
    )
    conn.commit()
    conn.close()


def insert_portal_request(
    user_id: Optional[int],
    full_name: str,
    email: str,
    phone: str,
    faculty: str,
    portal_section: str,
    issue_type: str,
    description: str,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO portal_requests (
            user_id, full_name, email, phone,
            faculty, portal_section, issue_type, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, full_name, email, phone, faculty, portal_section, issue_type, description),
    )
    conn.commit()
    conn.close()


def get_all_portal_requests() -> List[Tuple]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at, full_name, email, phone,
               faculty, portal_section, issue_type, description, status
        FROM portal_requests
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def update_portal_status(req_id: int, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE portal_requests SET status = ? WHERE id = ?",
        (status, req_id),
    )
    conn.commit()
    conn.close()


def delete_portal_request(req_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM portal_requests WHERE id = ?",
        (req_id,),
    )
    conn.commit()
    conn.close()
