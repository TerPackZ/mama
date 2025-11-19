import sqlite3
from typing import List, Tuple  # ← добавляем ЭТО

CERT_DB_PATH = "cert_requests.db"


def get_conn():
    return sqlite3.connect(CERT_DB_PATH)


def init_cert_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS cert_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            cert_type TEXT,
            full_name TEXT NOT NULL,
            birth_date TEXT,
            student_id TEXT,
            faculty TEXT,
            program TEXT,
            course TEXT,
            form_of_study TEXT,
            funding TEXT,
            period_from TEXT,
            period_to TEXT,
            language TEXT,
            pickup_method TEXT,
            email TEXT,
            phone TEXT,
            comment TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_cert_request(
    cert_type: str,
    full_name: str,
    birth_date: str,
    student_id: str,
    faculty: str,
    program: str,
    course: str,
    form_of_study: str,
    funding: str,
    period_from: str,
    period_to: str,
    language: str,
    pickup_method: str,
    email: str,
    phone: str,
    comment: str,
):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO cert_requests (
            cert_type, full_name, birth_date, student_id,
            faculty, program, course, form_of_study,
            funding, period_from, period_to,
            language, pickup_method, email, phone, comment
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cert_type,
            full_name,
            birth_date,
            student_id,
            faculty,
            program,
            course,
            form_of_study,
            funding,
            period_from,
            period_to,
            language,
            pickup_method,
            email,
            phone,
            comment,
        ),
    )
    conn.commit()
    conn.close()

def get_all_cert_requests() -> List[Tuple]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, created_at, cert_type, full_name, birth_date,
               student_id, faculty, program, course,
               form_of_study, funding, period_from, period_to,
               language, pickup_method, email, phone, comment
        FROM cert_requests
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()
    return rows