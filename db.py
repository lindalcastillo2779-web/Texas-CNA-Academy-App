"""Database initialisation and helper functions for Texas CNA Academy."""

import hashlib
import json
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

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

PORTAL_DATA_DIR = os.path.join(os.path.dirname(__file__), "public", "portal-data")
RENEWAL_HOURS_REQUIRED = 24.0
COURSE_MODULE_COUNT = 14
PASSWORD_HASH_ITERATIONS = 390000
PORTAL_SESSION_DAYS = 7
_PORTAL_DOMAIN_KEY_BY_NAME = {
    "Role of the Nurse Aide": "ROLE",
    "Safety and Emergency": "SAFETY",
    "Infection Control": "INFECT",
    "Psychosocial Care Skills": "PSYCHOSOCIAL",
    "Physical Care Skills": "SKILLS",
}


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
    phone       TEXT,
    facility    TEXT,
    password_hash TEXT,
    subscription_active INTEGER NOT NULL DEFAULT 0,
    last_login_at TEXT,
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

CREATE TABLE IF NOT EXISTS community_profiles (
    user_id                 INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    city                    TEXT,
    organization            TEXT,
    can_mentor              INTEGER NOT NULL DEFAULT 0,
    wants_mentor            INTEGER NOT NULL DEFAULT 0,
    open_to_opportunities   INTEGER NOT NULL DEFAULT 1,
    interest_areas          TEXT,
    availability            TEXT,
    bio                     TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS community_posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER REFERENCES users(id) ON DELETE SET NULL,
    post_type       TEXT NOT NULL CHECK (
        post_type IN ('mentor_request', 'mentor_offer', 'study_group', 'practice_partner', 'opportunity')
    ),
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    location        TEXT,
    contact_info    TEXT,
    tags            TEXT,
    audience_roles  TEXT,
    status          TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS portal_sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token_hash  TEXT NOT NULL UNIQUE,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    expires_at          TEXT NOT NULL,
    last_seen_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_portal_sessions_user_id
    ON portal_sessions(user_id);

CREATE INDEX IF NOT EXISTS idx_portal_sessions_expires_at
    ON portal_sessions(expires_at);
"""


def init_db() -> None:
    """Create tables and seed sample exam questions if the DB is new."""
    with get_conn() as conn:
        conn.executescript(_DDL)
        _migrate_user_subscription_fields(conn)
        _migrate_user_auth_fields(conn)
        _seed_questions(conn)
        _seed_community_posts(conn)
    _export_portal_snapshots()


def _migrate_user_subscription_fields(conn: sqlite3.Connection) -> None:
    """Ensure legacy databases contain required user subscription fields."""
    cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(users)").fetchall()
    }
    if "subscription_active" not in cols:
        conn.execute(
            "ALTER TABLE users ADD COLUMN subscription_active INTEGER NOT NULL DEFAULT 0"
        )


def _migrate_user_auth_fields(conn: sqlite3.Connection) -> None:
    """Ensure legacy databases contain required auth/profile fields."""
    cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(users)").fetchall()
    }
    if "phone" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    if "facility" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN facility TEXT")
    if "password_hash" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "last_login_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT")


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


_SAMPLE_COMMUNITY_POSTS = [
    (
        None,
        "mentor_offer",
        "Experienced CNA mentor available for exam-readiness coaching",
        "Get practical guidance on exam pacing, hand hygiene, transfer safety, and how to stay calm on test day.",
        "Dallas / Virtual",
        "Introduce yourself in the Community Hub and mention your goal.",
        "exam prep, infection control, skills lab",
        "student,cna",
        "active",
    ),
    (
        None,
        "study_group",
        "Weekly infection control study circle",
        "Small-group review for PPE, isolation precautions, and safety questions with accountability check-ins.",
        "Houston / Virtual",
        "Use the Community Hub board to request the next session invite.",
        "infection control, quiz review, study group",
        "student,instructor",
        "active",
    ),
    (
        None,
        "practice_partner",
        "Practice partner search for Prometric clinical skills",
        "Pair up to rehearse vital signs, transfer setup, communication scripts, and step sequencing before lab day.",
        "San Antonio",
        "Post your availability window and preferred practice skill.",
        "clinical skills, transfer, vital signs",
        "student,cna",
        "active",
    ),
    (
        None,
        "opportunity",
        "Facility shadow day and entry-level hiring event",
        "Meet facility leaders, learn workflow expectations, and explore openings for motivated CNA candidates.",
        "Fort Worth",
        "Bring your CNA documents and a short introduction about your goals.",
        "workforce, hiring, facility",
        "student,cna,facility",
        "active",
    ),
]


def _seed_community_posts(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM community_posts").fetchone()[0]
    if count > 0:
        return
    conn.executemany(
        """INSERT INTO community_posts
           (user_id, post_type, title, description, location, contact_info, tags, audience_roles, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        _SAMPLE_COMMUNITY_POSTS,
    )


def _split_tokens(value: str | None) -> set[str]:
    return {
        token.strip().lower()
        for token in (value or "").split(",")
        if token.strip()
    }


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------
def _utc_sql_timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def normalize_role(role: str | None) -> str:
    return (role or "student").strip().lower() or "student"


def split_name(name: str) -> tuple[str, str]:
    parts = [part for part in name.strip().split() if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        PASSWORD_HASH_ITERATIONS,
    )
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${password_salt}${derived_key.hex()}"


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        algorithm, iterations, salt, expected_hash = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(derived_key, expected_hash)


def _hash_session_token(session_token: str) -> str:
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def get_or_create_user(name: str, email: str, role: str = "student") -> int:
    """Return the user-id for *email*, creating the row if needed."""
    email = normalize_email(email)
    role = normalize_role(role)
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute(
            "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
            (name, email, role),
        )
        user_id = cur.lastrowid
    _export_portal_snapshots()
    return user_id


def get_user_by_email(email: str):
    email = normalize_email(email)
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    """Return a single user row by id, or None when not found."""
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_or_claim_user_account(
    *,
    name: str,
    email: str,
    password: str,
    role: str = "student",
    phone: str = "",
    facility: str = "",
) -> sqlite3.Row:
    email = normalize_email(email)
    role = normalize_role(role)
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if existing and existing["password_hash"]:
            raise ValueError("An account already exists for that email.")

        password_hash = _hash_password(password)
        normalized_name = name.strip()
        normalized_phone = phone.strip()
        normalized_facility = facility.strip()

        if existing:
            conn.execute(
                """
                UPDATE users
                SET name = ?, role = ?, phone = ?, facility = ?, password_hash = ?
                WHERE id = ?
                """,
                (
                    normalized_name,
                    role,
                    normalized_phone,
                    normalized_facility,
                    password_hash,
                    existing["id"],
                ),
            )
            user_id = int(existing["id"])
        else:
            cur = conn.execute(
                """
                INSERT INTO users (name, email, role, phone, facility, password_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_name,
                    email,
                    role,
                    normalized_phone,
                    normalized_facility,
                    password_hash,
                ),
            )
            user_id = int(cur.lastrowid)

    _export_portal_snapshots()
    user = get_user_by_id(user_id)
    if user is None:
        raise ValueError("Unable to load the created account.")
    return user


def authenticate_user(email: str, password: str) -> sqlite3.Row | None:
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (_utc_sql_timestamp(), user["id"]),
        )
    return get_user_by_id(int(user["id"]))


def create_portal_session(user_id: int, duration_days: int = PORTAL_SESSION_DAYS) -> str:
    cleanup_expired_portal_sessions()
    session_token = secrets.token_urlsafe(32)
    expires_at = _utc_sql_timestamp(datetime.now(timezone.utc) + timedelta(days=duration_days))
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO portal_sessions (user_id, session_token_hash, expires_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, _hash_session_token(session_token), expires_at, _utc_sql_timestamp()),
        )
    return session_token


def cleanup_expired_portal_sessions() -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM portal_sessions WHERE expires_at <= datetime('now')")


def delete_portal_session(session_token: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM portal_sessions WHERE session_token_hash = ?",
            (_hash_session_token(session_token),),
        )


def get_user_by_session_token(session_token: str) -> sqlite3.Row | None:
    cleanup_expired_portal_sessions()
    token_hash = _hash_session_token(session_token)
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT u.*
            FROM portal_sessions ps
            JOIN users u ON u.id = ps.user_id
            WHERE ps.session_token_hash = ? AND ps.expires_at > datetime('now')
            """,
            (token_hash,),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE portal_sessions SET last_seen_at = ? WHERE session_token_hash = ?",
                (_utc_sql_timestamp(), token_hash),
            )
        return row


def get_portal_profile(user: sqlite3.Row | dict) -> dict:
    first_name, last_name = split_name(str(user["name"]))
    return {
        "firstName": first_name,
        "lastName": last_name,
        "email": user["email"],
        "phone": user["phone"] or "",
        "role": user["role"],
        "facility": user["facility"] or "",
        "name": user["name"],
    }


def is_admin_role(role: str | None) -> bool:
    return normalize_role(role) == "admin"


def is_staff_role(role: str | None) -> bool:
    return normalize_role(role) in {"staff", "instructor", "don", "admin"}


def is_student_role(role: str | None) -> bool:
    return not is_staff_role(role)


def get_portal_dashboard_path(role: str | None) -> str:
    normalized_role = normalize_role(role)
    if is_admin_role(normalized_role):
        return "/admin-dashboard.html"
    if is_staff_role(normalized_role):
        return "/staff-dashboard.html"
    return "/dashboard.html"


def set_subscription_active(user_id: int, active: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET subscription_active = ? WHERE id = ?",
            (int(active), user_id),
        )
    _export_portal_snapshots()


def get_access_status(user_id: int, trial_days: int = 30) -> dict:
    """Return access details.

    Keys:
    - allowed: bool, whether user can access protected sections
    - subscribed: bool, whether subscription is active
    - trial_active: bool, whether free trial is still active
    - days_left: int, number of whole days left in trial
    - trial_ends_on: ISO date string for trial end, or None
    """
    user = get_user_by_id(user_id)
    if not user:
        return {
            "allowed": False,
            "subscribed": False,
            "trial_active": False,
            "days_left": 0,
            "trial_ends_on": None,
        }

    created_raw = user["created_at"] or ""
    created_valid = True
    try:
        created_at = datetime.fromisoformat(created_raw)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at.astimezone(timezone.utc)
    except ValueError:
        created_at = datetime.now(timezone.utc)
        created_valid = False

    now = datetime.now(timezone.utc)
    trial_ends = created_at + timedelta(days=trial_days)
    subscribed = bool(user["subscription_active"])
    trial_active = created_valid and now <= trial_ends
    days_left = max((trial_ends.date() - now.date()).days, 0)

    return {
        "allowed": subscribed or trial_active,
        "subscribed": subscribed,
        "trial_active": trial_active,
        "days_left": days_left,
        "trial_ends_on": trial_ends.date().isoformat(),
    }


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
    _export_portal_snapshots()


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
    _export_portal_snapshots()


def get_quiz_history(user_id: int) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT domain, score, total, taken_at
               FROM quiz_attempts WHERE user_id = ? ORDER BY taken_at DESC LIMIT 20""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_quiz_stats_by_domain(user_id: int) -> list[dict]:
    """Return per-domain quiz stats for a user.

    Each dict has keys: domain, attempts, avg_pct, best_pct, total_questions.
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                domain,
                COUNT(*) AS attempts,
                ROUND(AVG(CAST(score AS REAL) / CAST(total AS REAL) * 100), 1) AS avg_pct,
                ROUND(MAX(CAST(score AS REAL) / CAST(total AS REAL) * 100), 1) AS best_pct,
                SUM(total) AS total_questions
            FROM quiz_attempts
            WHERE user_id = ? AND domain IS NOT NULL AND total > 0
            GROUP BY domain
            ORDER BY avg_pct DESC
            """,
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_quiz_trend(user_id: int, limit: int = 30) -> list[dict]:
    """Return the last *limit* quiz attempts with their percentage score and date.

    Results are in chronological order (oldest first) so they can be plotted
    as a left-to-right trend line.  Each dict has keys: taken_at (ISO str),
    pct (float), domain (str).
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT taken_at, domain,
                   ROUND(CAST(score AS REAL) / CAST(total AS REAL) * 100, 1) AS pct
            FROM (
                SELECT taken_at, domain, score, total
                FROM quiz_attempts
                WHERE user_id = ? AND total > 0
                ORDER BY taken_at DESC
                LIMIT ?
            )
            ORDER BY taken_at ASC
            """,
            (user_id, limit),
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
    _export_portal_snapshots()


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


def get_staff_demand_summary(limit: int = 5) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                facility_name,
                COUNT(*) AS shifts_logged,
                SUM(CASE WHEN compliant = 0 THEN 1 ELSE 0 END) AS non_compliant_shifts,
                MAX(shift_date) AS latest_shift_date
            FROM staff_records
            GROUP BY facility_name
            ORDER BY shifts_logged DESC, latest_shift_date DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_community_profile(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT cp.*, u.name, u.role
            FROM community_profiles cp
            JOIN users u ON u.id = cp.user_id
            WHERE cp.user_id = ?
            """,
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def upsert_community_profile(
    user_id: int,
    city: str = "",
    organization: str = "",
    can_mentor: bool = False,
    wants_mentor: bool = False,
    open_to_opportunities: bool = True,
    interest_areas: str = "",
    availability: str = "",
    bio: str = "",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO community_profiles
                (user_id, city, organization, can_mentor, wants_mentor, open_to_opportunities,
                 interest_areas, availability, bio, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                city = excluded.city,
                organization = excluded.organization,
                can_mentor = excluded.can_mentor,
                wants_mentor = excluded.wants_mentor,
                open_to_opportunities = excluded.open_to_opportunities,
                interest_areas = excluded.interest_areas,
                availability = excluded.availability,
                bio = excluded.bio,
                updated_at = datetime('now')
            """,
            (
                user_id,
                city.strip(),
                organization.strip(),
                int(can_mentor),
                int(wants_mentor),
                int(open_to_opportunities),
                interest_areas.strip(),
                availability.strip(),
                bio.strip(),
            ),
        )
    _export_portal_snapshots()


def list_community_profiles(
    exclude_user_id: int | None = None,
    mentors_only: bool = False,
    limit: int = 20,
) -> list[dict]:
    clauses = []
    params: list[object] = []
    if exclude_user_id is not None:
        clauses.append("cp.user_id != ?")
        params.append(exclude_user_id)
    if mentors_only:
        clauses.append("cp.can_mentor = 1")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
        SELECT cp.*, u.name, u.role
        FROM community_profiles cp
        JOIN users u ON u.id = cp.user_id
        {where}
        ORDER BY cp.updated_at DESC
        LIMIT ?
    """
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def create_community_post(
    user_id: int | None,
    post_type: str,
    title: str,
    description: str,
    location: str = "",
    contact_info: str = "",
    tags: str = "",
    audience_roles: str = "",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO community_posts
                (user_id, post_type, title, description, location, contact_info, tags, audience_roles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                post_type,
                title.strip(),
                description.strip(),
                location.strip(),
                contact_info.strip(),
                tags.strip(),
                audience_roles.strip(),
            ),
        )
    _export_portal_snapshots()


def get_community_posts(
    post_type: str | None = None,
    status: str | None = "active",
    limit: int = 50,
) -> list[dict]:
    clauses = []
    params: list[object] = []
    if post_type:
        clauses.append("cp.post_type = ?")
        params.append(post_type)
    if status:
        clauses.append("cp.status = ?")
        params.append(status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"""
        SELECT
            cp.*,
            u.name AS author_name,
            u.role AS author_role
        FROM community_posts cp
        LEFT JOIN users u ON u.id = cp.user_id
        {where}
        ORDER BY cp.created_at DESC
        LIMIT ?
    """
    params.append(limit)
    with get_conn() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def get_user_community_posts(user_id: int, limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM community_posts
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def set_community_post_status(post_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE community_posts SET status = ? WHERE id = ?",
            (status, post_id),
        )
    _export_portal_snapshots()


def get_community_dashboard_counts() -> dict:
    with get_conn() as conn:
        mentors = conn.execute(
            "SELECT COUNT(*) FROM community_profiles WHERE can_mentor = 1"
        ).fetchone()[0]
        mentees = conn.execute(
            "SELECT COUNT(*) FROM community_profiles WHERE wants_mentor = 1"
        ).fetchone()[0]
        opportunities = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE post_type = 'opportunity' AND status = 'active'"
        ).fetchone()[0]
        study_groups = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE post_type = 'study_group' AND status = 'active'"
        ).fetchone()[0]
        total_posts = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE status = 'active'"
        ).fetchone()[0]
    return {
        "mentors": int(mentors),
        "mentees": int(mentees),
        "opportunities": int(opportunities),
        "study_groups": int(study_groups),
        "active_posts": int(total_posts),
    }


def get_mentor_matches(user_id: int, limit: int = 4) -> list[dict]:
    user = get_user_by_id(user_id)
    if not user:
        return []
    profile = get_community_profile(user_id) or {}
    weak_domains = {
        stat["domain"].lower()
        for stat in get_quiz_stats_by_domain(user_id)
        if float(stat.get("avg_pct") or 0) < 75
    }
    user_interests = _split_tokens(profile.get("interest_areas"))
    matches: list[tuple[int, dict]] = []
    for candidate in list_community_profiles(exclude_user_id=user_id, mentors_only=True, limit=25):
        score = 1
        candidate_interests = _split_tokens(candidate.get("interest_areas"))
        score += len(weak_domains & candidate_interests) * 3
        score += len(user_interests & candidate_interests) * 2
        if candidate.get("role") in {"cna", "instructor", "don"}:
            score += 2
        if profile.get("wants_mentor"):
            score += 2
        matches.append((score, candidate))
    matches.sort(key=lambda item: (-item[0], item[1].get("updated_at", "")))
    return [candidate for _, candidate in matches[:limit]]


def get_recommended_posts_for_user(user_id: int, limit: int = 6) -> list[dict]:
    user = get_user_by_id(user_id)
    if not user:
        return []
    profile = get_community_profile(user_id) or {}
    preferred_tokens = _split_tokens(profile.get("interest_areas"))
    weak_domains = {
        stat["domain"].lower()
        for stat in get_quiz_stats_by_domain(user_id)
        if float(stat.get("avg_pct") or 0) < 75
    }
    preferred_tokens.update(weak_domains)
    posts = get_community_posts(status="active", limit=40)
    ranked: list[tuple[int, dict]] = []
    for post in posts:
        score = 1
        post_tags = _split_tokens(post.get("tags"))
        audience_roles = _split_tokens(post.get("audience_roles"))
        if post["post_type"] == "opportunity" and profile.get("open_to_opportunities", 1):
            score += 3
        if post["post_type"] == "mentor_offer" and (profile.get("wants_mentor") or user["role"] == "student"):
            score += 3
        if post["post_type"] == "study_group" and user["role"] in {"student", "instructor"}:
            score += 2
        if not audience_roles or user["role"].lower() in audience_roles:
            score += 2
        score += len(preferred_tokens & post_tags) * 2
        ranked.append((score, post))
    ranked.sort(key=lambda item: (-item[0], item[1].get("created_at", "")))
    return [post for _, post in ranked[:limit]]


def get_recommended_community_actions(user_id: int) -> list[str]:
    user = get_user_by_id(user_id)
    if not user:
        return []
    profile = get_community_profile(user_id) or {}
    weak_domains = [
        stat["domain"]
        for stat in get_quiz_stats_by_domain(user_id)
        if float(stat.get("avg_pct") or 0) < 75
    ]
    ceu_remaining = max(0.0, 24.0 - total_ceu_hours(user_id))
    posts = get_user_community_posts(user_id, limit=5)
    actions: list[str] = []
    if user["role"] == "student" and weak_domains:
        actions.append(f"Ask for mentoring in {weak_domains[0]} to turn your weakest quiz area into a study plan.")
    if not profile:
        actions.append("Complete your Community Hub profile so mentors, instructors, and facilities can find the right fit.")
    if profile and not profile.get("wants_mentor") and user["role"] == "student":
        actions.append("Turn on mentor matching to get support from experienced CNAs or instructors.")
    if ceu_remaining > 0 and user["role"] in {"cna", "don", "instructor"}:
        actions.append(f"You still need {ceu_remaining:.1f} CEU hours — follow opportunity posts that include renewal-friendly training.")
    if not posts:
        actions.append("Create your first post so the community can respond with practice, study, or workforce support.")
    if not actions:
        actions.append("Review a mentor match or opportunity post today to keep your network active.")
    return actions[:4]


def _calculate_readiness_score(stats: list[dict]) -> float:
    total_questions = sum(int(stat.get("total_questions") or 0) for stat in stats)
    if total_questions <= 0:
        return 0.0
    weighted_sum = sum(
        float(stat.get("avg_pct") or 0) * int(stat.get("total_questions") or 0)
        for stat in stats
    )
    return round(weighted_sum / total_questions, 1)


def _get_last_user_activity(user_id: int, created_at: str | None) -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT MAX(activity_at) AS last_activity
            FROM (
                SELECT created_at AS activity_at FROM users WHERE id = ?
                UNION ALL
                SELECT taken_at FROM quiz_attempts WHERE user_id = ?
                UNION ALL
                SELECT created_at FROM ceu_records WHERE user_id = ?
                UNION ALL
                SELECT updated_at FROM community_profiles WHERE user_id = ?
                UNION ALL
                SELECT created_at FROM community_posts WHERE user_id = ?
            )
            """,
            (user_id, user_id, user_id, user_id, user_id),
        ).fetchone()
    return (row["last_activity"] if row and row["last_activity"] else None) or created_at


def _build_student_portal_record(user: dict) -> dict:
    user_id = int(user["id"])
    access = get_access_status(user_id)
    ceu_records = get_ceu_records(user_id)
    earned_hours = total_ceu_hours(user_id)
    quiz_stats = get_quiz_stats_by_domain(user_id)
    quiz_history = get_quiz_history(user_id)
    readiness_score = _calculate_readiness_score(quiz_stats)
    weakest_stat = min(quiz_stats, key=lambda stat: float(stat.get("avg_pct") or 0)) if quiz_stats else None
    strongest_stat = max(quiz_stats, key=lambda stat: float(stat.get("avg_pct") or 0)) if quiz_stats else None

    if access["subscribed"]:
        status_chip = "Subscription active"
    elif access["trial_active"]:
        status_chip = f"{access['days_left']} day trial left"
    else:
        status_chip = "Subscription required"

    weakest_domain_key = (
        _PORTAL_DOMAIN_KEY_BY_NAME.get(weakest_stat["domain"], "INFECT")
        if weakest_stat is not None
        else "INFECT"
    )
    strongest_domain_key = (
        _PORTAL_DOMAIN_KEY_BY_NAME.get(strongest_stat["domain"], "ROLE")
        if strongest_stat is not None
        else "ROLE"
    )

    return {
        "id": user_id,
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "statusChip": status_chip,
        "access": access,
        "ceu": {
            "earnedHours": round(earned_hours, 1),
            "requiredHours": RENEWAL_HOURS_REQUIRED,
            "remainingHours": round(max(0.0, RENEWAL_HOURS_REQUIRED - earned_hours), 1),
            "recentRecords": ceu_records[:5],
        },
        "quiz": {
            "readinessScore": readiness_score,
            "totalAttempts": len(quiz_history),
            "totalQuestions": sum(int(stat.get("total_questions") or 0) for stat in quiz_stats),
            "weakestDomainKey": weakest_domain_key,
            "strongestDomainKey": strongest_domain_key,
            "statsByDomain": [
                {
                    "domain": stat["domain"],
                    "avgPct": float(stat.get("avg_pct") or 0),
                    "bestPct": float(stat.get("best_pct") or 0),
                    "attempts": int(stat.get("attempts") or 0),
                }
                for stat in quiz_stats
            ],
            "recentAttempts": [
                {
                    "domain": attempt["domain"],
                    "pct": round((attempt["score"] / attempt["total"]) * 100, 1) if attempt["total"] else 0.0,
                    "takenAt": attempt["taken_at"],
                }
                for attempt in quiz_history[:5]
            ],
        },
        "community": {
            "recommendedActions": get_recommended_community_actions(user_id),
            "mentorMatches": get_mentor_matches(user_id),
            "recommendedPosts": get_recommended_posts_for_user(user_id),
        },
    }


def build_student_portal_payload(user_id: int) -> dict | None:
    user = get_user_by_id(user_id)
    if user is None:
        return None
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "profile": get_portal_profile(user),
        "student": _build_student_portal_record(dict(user)),
    }


def _build_student_portal_snapshot() -> dict:
    with get_conn() as conn:
        users = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, name, email, role, created_at
                FROM users
                WHERE role IN ('student', 'cna', 'don', 'instructor', 'facility')
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        ]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "students": [_build_student_portal_record(user) for user in users],
    }


def build_staff_portal_payload() -> dict:
    return _build_staff_portal_snapshot()


def _build_staff_portal_snapshot() -> dict:
    with get_conn() as conn:
        users = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, name, email, role, created_at
                FROM users
                WHERE role IN ('student', 'cna', 'instructor', 'don')
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        ]
        mentor_request_count = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE post_type = 'mentor_request' AND status = 'active'"
        ).fetchone()[0]
        study_group_count = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE post_type = 'study_group' AND status = 'active'"
        ).fetchone()[0]
        opportunity_count = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE post_type = 'opportunity' AND status = 'active'"
        ).fetchone()[0]

    learners = [user for user in users if user["role"] in {"student", "cna"}]
    roster: list[dict] = []
    grade_book: list[dict] = []
    readiness_scores: list[float] = []
    passing_learners = 0

    for learner in learners:
        learner_record = _build_student_portal_record(learner)
        readiness = float(learner_record["quiz"]["readinessScore"])
        attempts = int(learner_record["quiz"]["totalAttempts"])
        if attempts > 0:
            readiness_scores.append(readiness)
            if readiness >= 70:
                passing_learners += 1
        roster.append(
            {
                "name": learner["name"],
                "email": learner["email"],
                "progress": round(readiness),
                "lastActiveAt": _get_last_user_activity(learner["id"], learner.get("created_at")),
                "status": "On track" if readiness >= 70 and attempts > 0 else "Needs attention",
            }
        )
        recent_attempts = learner_record["quiz"]["recentAttempts"]
        percentages = [float(attempt["pct"]) for attempt in recent_attempts[:2]]
        average = round(sum(percentages) / len(percentages)) if percentages else 0
        grade_book.append(
            {
                "name": learner["name"],
                "exam1": f"{round(percentages[0])}%" if len(percentages) >= 1 else "—",
                "exam2": f"{round(percentages[1])}%" if len(percentages) >= 2 else "—",
                "average": f"{average}%" if percentages else "—",
            }
        )

    facility_summary = [
        {
            "day": "LIVE",
            "title": facility["facility_name"],
            "detail": (
                f"{facility['shifts_logged']} shifts logged · latest {facility['latest_shift_date']}"
            ),
            "status": (
                "Needs support" if facility["non_compliant_shifts"] else "Compliant"
            ),
        }
        for facility in get_staff_demand_summary(limit=5)
    ]

    readiness_average = round(sum(readiness_scores) / len(readiness_scores)) if readiness_scores else 0
    passing_rate = round((passing_learners / len(readiness_scores)) * 100) if readiness_scores else 0

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "studentMetrics": [
            {
                "label": "Total students",
                "value": str(len(learners)),
                "detail": "Connected learner accounts in the live database.",
            },
            {
                "label": "Passing rate",
                "value": f"{passing_rate}%",
                "detail": "Based on learners with recorded quiz attempts.",
            },
            {
                "label": "Average readiness",
                "value": f"{readiness_average}%",
                "detail": "Weighted from each learner's quiz history.",
            },
        ],
        "studentRoster": roster[:12],
        "facilitySchedule": facility_summary,
        "gradeBook": grade_book[:12],
        "communityQueue": [
            {
                "title": f"{mentor_request_count} mentor request(s) are active",
                "detail": "Use the live community board to follow up with learners asking for support.",
                "status": "Action needed" if mentor_request_count else "Stable",
            },
            {
                "title": f"{study_group_count} study group post(s) are live",
                "detail": "Review whether the current study circles match the next quiz and skills priorities.",
                "status": "Open" if study_group_count else "Quiet",
            },
            {
                "title": f"{opportunity_count} workforce opportunity post(s) are visible",
                "detail": "Share job-ready learners with facilities when opportunities align.",
                "status": "Partnership" if opportunity_count else "Monitor",
            },
        ],
    }


def build_admin_portal_payload() -> dict:
    return _build_admin_portal_snapshot()


def _build_admin_recent_activity() -> list[dict]:
    events: list[dict] = []
    with get_conn() as conn:
        for row in conn.execute(
            "SELECT name, role, created_at FROM users ORDER BY created_at DESC LIMIT 4"
        ).fetchall():
            events.append(
                {
                    "title": f"New {row['role']} account: {row['name']}",
                    "detail": row["created_at"],
                    "tone": "is-success",
                }
            )
        for row in conn.execute(
            """
            SELECT course_name, completed_on, hours
            FROM ceu_records
            ORDER BY created_at DESC
            LIMIT 3
            """
        ).fetchall():
            events.append(
                {
                    "title": f"CEU logged: {row['course_name']}",
                    "detail": f"{row['hours']} hour(s) · {row['completed_on']}",
                    "tone": "is-muted",
                }
            )
        for row in conn.execute(
            """
            SELECT title, post_type, created_at
            FROM community_posts
            ORDER BY created_at DESC
            LIMIT 3
            """
        ).fetchall():
            events.append(
                {
                    "title": f"Community post: {row['title']}",
                    "detail": f"{row['post_type']} · {row['created_at']}",
                    "tone": "is-warning",
                }
            )
    events.sort(key=lambda item: item["detail"], reverse=True)
    return events[:6]


def _build_admin_portal_snapshot() -> dict:
    with get_conn() as conn:
        users = [
            dict(row)
            for row in conn.execute(
                "SELECT id, name, email, role, subscription_active, created_at FROM users ORDER BY created_at DESC, id DESC LIMIT 30"
            ).fetchall()
        ]
        total_students = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role IN ('student', 'cna')"
        ).fetchone()[0]
        total_instructors = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role IN ('instructor', 'don')"
        ).fetchone()[0]
        question_count = conn.execute(
            "SELECT COUNT(*) FROM exam_questions"
        ).fetchone()[0]
        active_posts = conn.execute(
            "SELECT COUNT(*) FROM community_posts WHERE status = 'active'"
        ).fetchone()[0]
        mentor_profiles = conn.execute(
            "SELECT COUNT(*) FROM community_profiles WHERE can_mentor = 1"
        ).fetchone()[0]
        non_compliant_shifts = conn.execute(
            "SELECT COUNT(*) FROM staff_records WHERE compliant = 0"
        ).fetchone()[0]
        review_queue = [
            dict(row)
            for row in conn.execute(
                """
                SELECT title, post_type, status, created_at
                FROM community_posts
                ORDER BY created_at DESC
                LIMIT 3
                """
            ).fetchall()
        ]

    learner_records = [
        _build_student_portal_record(user)
        for user in users
        if user["role"] in {"student", "cna"}
    ]
    readiness_scores = [
        float(record["quiz"]["readinessScore"])
        for record in learner_records
        if int(record["quiz"]["totalAttempts"]) > 0
    ]
    passing_rate = round(
        (sum(1 for score in readiness_scores if score >= 70) / len(readiness_scores)) * 100
    ) if readiness_scores else 0
    pending_reviews = sum(1 for post in review_queue if post["status"] == "active")

    active_access_count = 0
    renewal_ready_count = 0
    renewal_pending_count = 0
    for user in users:
        access = get_access_status(user["id"])
        if access["allowed"]:
            active_access_count += 1
        if user["role"] in {"cna", "don", "instructor"}:
            remaining = max(0.0, RENEWAL_HOURS_REQUIRED - total_ceu_hours(user["id"]))
            if remaining == 0:
                renewal_ready_count += 1
            else:
                renewal_pending_count += 1

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "overviewMetrics": [
            {
                "label": "Total students",
                "value": str(total_students),
                "detail": "Student and CNA learner accounts in the live database.",
            },
            {
                "label": "Active instructors",
                "value": str(total_instructors),
                "detail": "Instructor and DON accounts currently registered.",
            },
            {
                "label": "Live course modules",
                "value": str(COURSE_MODULE_COUNT),
                "detail": "React portals are aligned to the full CNA course roadmap.",
            },
            {
                "label": "Pass rate",
                "value": f"{passing_rate}%",
                "detail": "Based on learners with recorded quiz attempts.",
            },
            {
                "label": "Pending reviews",
                "value": str(pending_reviews),
                "detail": "Recent community posts still visible in the moderation queue.",
            },
        ],
        "recentActivity": _build_admin_recent_activity(),
        "users": [
            {
                "name": user["name"],
                "role": str(user["role"]).title(),
                "email": user["email"],
                "status": "Active" if get_access_status(user["id"])["allowed"] else "Review",
            }
            for user in users[:12]
        ],
        "courses": [
            {
                "title": "CNA Certification Roadmap",
                "detail": f"{COURSE_MODULE_COUNT} modules · React student portal connected to live progress signals",
                "status": "Active",
                "meta": f"{total_students} learner accounts",
            },
            {
                "title": "Exam Prep Question Bank",
                "detail": f"{question_count} seeded practice questions in SQLite",
                "status": "Active",
                "meta": f"{len(readiness_scores)} learners with quiz history",
            },
            {
                "title": "Community + Workforce Hub",
                "detail": f"{active_posts} active posts · mentorship and opportunity routing",
                "status": "Active",
                "meta": f"{mentor_profiles} mentor profile(s)",
            },
        ],
        "compliance": [
            {"label": "Accounts with access", "value": str(active_access_count), "tone": "is-success"},
            {"label": "Renewals pending", "value": str(renewal_pending_count), "tone": "is-warning"},
            {"label": "Non-compliant shifts", "value": str(non_compliant_shifts), "tone": "is-danger" if non_compliant_shifts else "is-success"},
        ],
        "communityHealth": [
            {"label": "Mentor profiles", "value": str(mentor_profiles), "tone": "is-success"},
            {"label": "Active posts", "value": str(active_posts), "tone": "is-warning" if active_posts else "is-muted"},
            {"label": "Renewal-ready pros", "value": str(renewal_ready_count), "tone": "is-muted"},
        ],
        "communityReviewQueue": [
            {
                "title": post["title"],
                "detail": f"{post['post_type']} · {post['created_at']}",
                "tone": "is-warning" if post["status"] == "active" else "is-muted",
            }
            for post in review_queue
        ],
    }


def _write_portal_snapshot(filename: str, payload: dict) -> None:
    os.makedirs(PORTAL_DATA_DIR, exist_ok=True)
    path = os.path.join(PORTAL_DATA_DIR, filename)
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    os.replace(temp_path, path)


def _export_portal_snapshots() -> None:
    try:
        _write_portal_snapshot("student-dashboard.json", _build_student_portal_snapshot())
        _write_portal_snapshot("staff-dashboard.json", _build_staff_portal_snapshot())
        _write_portal_snapshot("admin-dashboard.json", _build_admin_portal_snapshot())
    except Exception as exc:  # pragma: no cover - defensive runtime sync
        print(f"[portal-data] snapshot export skipped: {exc}")
