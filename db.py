"""Database initialisation and helper functions for Texas CNA Academy."""

import os
import sqlite3
from contextlib import contextmanager

# ---------------------------------------------------------------------------
# Persistent-disk path detection (Render) vs local development fallback
# ---------------------------------------------------------------------------
_RENDER_DISK = "/data"
if os.path.isdir(_RENDER_DISK) and os.access(_RENDER_DISK, os.W_OK):
    DB_PATH = os.path.join(_RENDER_DISK, "cna_academy.db")
else:
    _local_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(_local_dir, exist_ok=True)
    DB_PATH = os.path.join(_local_dir, "cna_academy.db")


@contextmanager
def get_conn():
    """Yield a SQLite connection that closes automatically.

    Each call opens a fresh connection and closes it on exit, which is the
    standard thread-safe pattern for SQLite in Streamlit: one short-lived
    connection per request rather than a shared long-lived connection.
    check_same_thread=False is required because Streamlit may run the same
    session across threads; the context-manager scope ensures the connection
    is never shared between concurrent calls.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------
_DDL = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    role        TEXT    NOT NULL DEFAULT 'student',   -- student | cna | don | instructor | facility
    state_id    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ceu_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_name  TEXT    NOT NULL,
    provider     TEXT,
    hours        REAL    NOT NULL CHECK (hours > 0),
    completed_on TEXT    NOT NULL,
    certificate  TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exam_questions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    domain      TEXT    NOT NULL,
    question    TEXT    NOT NULL,
    option_a    TEXT    NOT NULL,
    option_b    TEXT    NOT NULL,
    option_c    TEXT    NOT NULL,
    option_d    TEXT    NOT NULL,
    correct     TEXT    NOT NULL CHECK (correct IN ('A','B','C','D')),
    explanation TEXT
);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    domain      TEXT,
    score       INTEGER NOT NULL,
    total       INTEGER NOT NULL,
    taken_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS staff_records (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_name TEXT NOT NULL,
    cna_name      TEXT NOT NULL,
    cna_state_id  TEXT,
    shift_date    TEXT NOT NULL,
    shift_type    TEXT NOT NULL,   -- day | evening | night
    hours_worked  REAL NOT NULL CHECK (hours_worked > 0),
    compliant     INTEGER NOT NULL DEFAULT 1,
    notes         TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db() -> None:
    """Create tables and seed sample exam questions if the DB is new."""
    with get_conn() as conn:
        conn.executescript(_DDL)
        _seed_questions(conn)


# ---------------------------------------------------------------------------
# Seeded practice questions (NATCEP domains)
# ---------------------------------------------------------------------------
_SAMPLE_QUESTIONS = [
    # Physical Care Skills
    ("Physical Care Skills",
     "When turning a patient to prevent pressure injuries, how often should repositioning occur?",
     "Every 4 hours", "Every 2 hours", "Every 8 hours", "Every 1 hour",
     "B", "Patients should be repositioned at least every 2 hours to relieve pressure on bony prominences."),
    ("Physical Care Skills",
     "Which of the following is the correct hand-washing technique step?",
     "Rinse hands before applying soap",
     "Scrub hands for at least 20 seconds",
     "Use hot water only",
     "Dry hands with a cloth towel shared among staff",
     "B", "Hands must be scrubbed for at least 20 seconds with soap and water."),
    ("Physical Care Skills",
     "When measuring a patient's blood pressure, the cuff should be placed:",
     "Over clothing for convenience",
     "On the upper arm, 1 inch above the antecubital fossa",
     "On the wrist, palm facing down",
     "As tight as possible to get an accurate reading",
     "B", "The BP cuff belongs on the bare upper arm about 1 inch above the antecubital space."),
    # Psychosocial Care Skills
    ("Psychosocial Care Skills",
     "A resident refuses to eat. The CNA's first action should be to:",
     "Force the resident to eat",
     "Report to the nurse immediately without speaking to the resident",
     "Ask the resident about their food preferences and report to the nurse",
     "Document the refusal and leave the room",
     "C", "Respecting autonomy while gathering information and notifying the nurse is the correct response."),
    ("Psychosocial Care Skills",
     "Which action BEST supports a resident's dignity?",
     "Discussing the resident's condition in the hallway",
     "Knocking and waiting before entering a resident's room",
     "Leaving the door open during personal care",
     "Referring to the resident by room number",
     "B", "Knocking and waiting respects privacy and dignity."),
    # Role of the Nurse Aide
    ("Role of the Nurse Aide",
     "A CNA witnesses a co-worker abusing a resident. The CNA should:",
     "Ignore it to avoid conflict",
     "Talk to the co-worker privately first",
     "Report the incident to the supervisor immediately",
     "Document the incident at the end of the shift",
     "C", "Abuse must be reported immediately to protect the resident."),
    ("Role of the Nurse Aide",
     "Which task is WITHIN the CNA's scope of practice in Texas?",
     "Administering oral medications",
     "Inserting a urinary catheter",
     "Measuring and recording vital signs",
     "Changing a sterile wound dressing independently",
     "C", "Measuring and recording vital signs is a standard CNA task."),
    # Safety and Emergency
    ("Safety and Emergency",
     "When using a gait belt, the CNA should:",
     "Apply it over the resident's clothing, snug but with space for two fingers",
     "Apply it directly on bare skin for best grip",
     "Tighten it as much as possible for safety",
     "Use it only for residents who can walk independently",
     "A", "The gait belt goes over clothing, snug enough to hold but with room for two fingers."),
    ("Safety and Emergency",
     "In the event of a fire, what is the RACE acronym order?",
     "Run, Alert, Contain, Extinguish",
     "Rescue, Alarm, Contain, Extinguish",
     "Report, Assist, Call, Evacuate",
     "Remove, Activate, Close, Extinguish",
     "B", "RACE: Rescue those in danger, Alarm, Contain the fire, Extinguish if safe to do so."),
    # Infection Control
    ("Infection Control",
     "Standard precautions apply to:",
     "Only patients with known infections",
     "Only blood and bodily fluids that are visibly bloody",
     "All patients, all body fluids, non-intact skin, and mucous membranes",
     "Patients on contact precautions only",
     "C", "Standard precautions apply universally to all patients regardless of diagnosis."),
    ("Infection Control",
     "Personal protective equipment (PPE) should be removed in which order?",
     "Mask, gloves, gown, goggles",
     "Gloves, goggles, gown, mask",
     "Gown, gloves, goggles, mask",
     "Goggles, gown, gloves, mask",
     "B", "The correct doffing order is gloves → goggles/face shield → gown → mask/respirator."),
]


def _seed_questions(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM exam_questions").fetchone()[0]
    if count > 0:
        return
    conn.executemany(
        """INSERT INTO exam_questions
           (domain, question, option_a, option_b, option_c, option_d, correct, explanation)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        _SAMPLE_QUESTIONS,
    )


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------
def get_or_create_user(name: str, email: str, role: str = "student") -> int:
    """Return the user-id for *email*, creating the row if needed."""
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
            (name, email, role),
        )
        return cur.lastrowid


def get_user_by_email(email: str):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


# ---------------------------------------------------------------------------
# CEU helpers
# ---------------------------------------------------------------------------
def add_ceu_record(user_id: int, course_name: str, provider: str,
                   hours: float, completed_on: str, certificate: str = "") -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO ceu_records (user_id, course_name, provider, hours, completed_on, certificate)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, course_name, provider, hours, completed_on, certificate),
        )


def get_ceu_records(user_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ceu_records WHERE user_id = ? ORDER BY completed_on DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def total_ceu_hours(user_id: int) -> float:
    with get_conn() as conn:
        result = conn.execute(
            "SELECT COALESCE(SUM(hours), 0) FROM ceu_records WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return float(result[0])


# ---------------------------------------------------------------------------
# Exam helpers
# ---------------------------------------------------------------------------
def get_questions_by_domain(domain: str | None = None, limit: int = 10) -> list:
    with get_conn() as conn:
        if domain and domain != "All Domains":
            rows = conn.execute(
                "SELECT * FROM exam_questions WHERE domain = ? ORDER BY RANDOM() LIMIT ?",
                (domain, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM exam_questions ORDER BY RANDOM() LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def get_domains() -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT domain FROM exam_questions ORDER BY domain"
        ).fetchall()
        return [r[0] for r in rows]


def save_quiz_attempt(user_id: int | None, domain: str | None,
                      score: int, total: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO quiz_attempts (user_id, domain, score, total) VALUES (?, ?, ?, ?)",
            (user_id, domain, score, total),
        )


def get_quiz_history(user_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT domain, score, total, taken_at
               FROM quiz_attempts WHERE user_id = ? ORDER BY taken_at DESC LIMIT 20""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Staffing helpers
# ---------------------------------------------------------------------------
def add_staff_record(facility: str, cna_name: str, cna_state_id: str,
                     shift_date: str, shift_type: str, hours: float,
                     compliant: bool = True, notes: str = "") -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO staff_records
               (facility_name, cna_name, cna_state_id, shift_date, shift_type,
                hours_worked, compliant, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (facility, cna_name, cna_state_id, shift_date, shift_type,
             hours, int(compliant), notes),
        )


def get_staff_records(facility: str | None = None) -> list:
    with get_conn() as conn:
        if facility:
            rows = conn.execute(
                "SELECT * FROM staff_records WHERE facility_name = ? ORDER BY shift_date DESC",
                (facility,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM staff_records ORDER BY shift_date DESC"
            ).fetchall()
        return [dict(r) for r in rows]
