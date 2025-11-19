import sqlite3
from typing import List, Tuple  # ← добавь это, если ещё нет

ECP_DB_PATH = "ecp_requests.db"


def get_conn():
    return sqlite3.connect(ECP_DB_PATH)


def get_all_ecp_requests() -> List[Tuple]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at,
               full_name, role, ecp_type, office,
               preferred_date, time_slot,
               email, phone, passport_last4, snils,
               comment, status
        FROM ecp_requests
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def init_ecp_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ecp_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            full_name TEXT NOT NULL,
            role TEXT,
            ecp_type TEXT,
            office TEXT,
            preferred_date TEXT,
            time_slot TEXT,
            email TEXT,
            phone TEXT,
            passport_last4 TEXT,
            snils TEXT,
            comment TEXT,
            status TEXT DEFAULT 'ожидает'
        )
        """
    )
    conn.commit()
    conn.close()


def insert_ecp_request(
    full_name: str,
    role: str,
    ecp_type: str,
    office: str,
    preferred_date: str,
    time_slot: str,
    email: str,
    phone: str,
    passport_last4: str,
    snils: str,
    comment: str,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO ecp_requests (
            full_name, role, ecp_type, office,
            preferred_date, time_slot,
            email, phone,
            passport_last4, snils, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            full_name,
            role,
            ecp_type,
            office,
            preferred_date,
            time_slot,
            email,
            phone,
            passport_last4,
            snils,
            comment,
        ),
    )
    conn.commit()
    conn.close()

def get_all_ecp_requests() -> List[Tuple]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at,
               full_name, role, ecp_type, office,
               preferred_date, time_slot,
               email, phone, passport_last4, snils,
               comment
        FROM ecp_requests
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows