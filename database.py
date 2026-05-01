import sqlite3
import pandas as pd
from datetime import datetime
import hashlib


DB_NAME = "smartfresh.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def add_column_if_missing(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # USERS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        status TEXT
    )
    """)

    # -----------------------------
    # ALERTS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        risk_type TEXT,
        batch_id TEXT,
        severity TEXT,
        issue TEXT,
        recommended_action TEXT,
        status TEXT,
        priority_score INTEGER,
        assigned_team TEXT,
        source TEXT
    )
    """)

    # -----------------------------
    # AGENT ACTIONS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        risk_type TEXT,
        batch_id TEXT,
        client TEXT,
        product TEXT,
        severity TEXT,
        issue TEXT,
        recommended_action TEXT,
        assigned_team TEXT,
        status TEXT,
        priority_score INTEGER,
        source_alert_id INTEGER,
        due_date TEXT,
        resolved_at TEXT
    )
    """)

    # -----------------------------
    # AGENT LOGS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        log_type TEXT,
        message TEXT,
        user_email TEXT
    )
    """)

    # -----------------------------
    # STREAM EVENTS TABLE
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stream_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        event_type TEXT,
        batch_id TEXT,
        severity TEXT,
        message TEXT,
        payload TEXT
    )
    """)

    # -----------------------------
    # SAFE MIGRATIONS FOR OLD DB
    # -----------------------------
    add_column_if_missing(cursor, "alerts", "priority_score", "INTEGER")
    add_column_if_missing(cursor, "alerts", "assigned_team", "TEXT")
    add_column_if_missing(cursor, "alerts", "source", "TEXT")

    add_column_if_missing(cursor, "agent_actions", "priority_score", "INTEGER")
    add_column_if_missing(cursor, "agent_actions", "source_alert_id", "INTEGER")
    add_column_if_missing(cursor, "agent_actions", "due_date", "TEXT")
    add_column_if_missing(cursor, "agent_actions", "resolved_at", "TEXT")

    add_column_if_missing(cursor, "agent_logs", "user_email", "TEXT")

    # -----------------------------
    # DEFAULT USERS
    # -----------------------------
    default_users = [
        ("Admin User", "admin@smartfresh.ai", "admin123", "Admin"),
        ("Manager User", "manager@smartfresh.ai", "manager123", "Manager"),
        ("Operations User", "operations@smartfresh.ai", "operations123", "Operations"),
        ("Quality User", "quality@smartfresh.ai", "quality123", "Quality"),
        ("Logistics User", "logistics@smartfresh.ai", "logistics123", "Logistics"),
    ]

    for name, email, password, role in default_users:
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("""
            INSERT INTO users (
                created_at,
                name,
                email,
                password_hash,
                role,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                now(),
                name,
                email,
                hash_password(password),
                role,
                "Active"
            ))

    conn.commit()
    conn.close()


# -----------------------------
# LOGIN / USER FUNCTIONS
# -----------------------------
def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, name, email, role, status
    FROM users
    WHERE email = ? AND password_hash = ?
    """, (email, hash_password(password)))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "status": user[4]
        }

    return None


def load_users():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, created_at, name, email, role, status FROM users ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df


# -----------------------------
# PRIORITY / TEAM LOGIC
# -----------------------------
def calculate_priority(alert):
    score = 0

    severity = str(alert.get("severity", "")).lower()
    risk_type = str(alert.get("risk_type", "")).lower()

    if severity == "high":
        score += 50
    elif severity == "medium":
        score += 30
    else:
        score += 10

    if "waste" in risk_type:
        score += 20
    if "delay" in risk_type:
        score += 20
    if "cold" in risk_type or "temperature" in risk_type:
        score += 20
    if "defect" in risk_type or "quality" in risk_type:
        score += 20
    if "revenue" in risk_type:
        score += 25
    if "schedule" in risk_type:
        score += 15

    return min(score, 100)


def assign_team(alert):
    risk_type = str(alert.get("risk_type", "")).lower()

    if "waste" in risk_type or "defect" in risk_type or "quality" in risk_type:
        return "Quality Team"
    if "delay" in risk_type:
        return "Logistics Team"
    if "cold" in risk_type or "temperature" in risk_type:
        return "Operations Team"
    if "revenue" in risk_type:
        return "Management Team"
    if "schedule" in risk_type:
        return "Operations Team"

    return "Operations Team"


# -----------------------------
# ALERT FUNCTIONS
# -----------------------------
def save_alert(alert, status="Open", source="AI Production Agent"):
    conn = get_connection()
    cursor = conn.cursor()

    priority_score = alert.get("priority_score", calculate_priority(alert))
    assigned_team = alert.get("assigned_team", assign_team(alert))

    cursor.execute("""
    INSERT INTO alerts (
        timestamp,
        risk_type,
        batch_id,
        severity,
        issue,
        recommended_action,
        status,
        priority_score,
        assigned_team,
        source
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now(),
        alert.get("risk_type", ""),
        alert.get("batch_id", ""),
        alert.get("severity", ""),
        alert.get("issue", ""),
        alert.get("recommended_action", ""),
        status,
        priority_score,
        assigned_team,
        source
    ))

    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return alert_id


def load_alerts():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM alerts ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def update_alert_status(alert_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE alerts
    SET status = ?
    WHERE id = ?
    """, (new_status, alert_id))

    conn.commit()
    conn.close()


# -----------------------------
# AGENT ACTION FUNCTIONS
# -----------------------------
def save_agent_action(
    alert,
    assigned_team=None,
    status="Open",
    source_alert_id=None,
    due_date=None
):
    conn = get_connection()
    cursor = conn.cursor()

    priority_score = alert.get("priority_score", calculate_priority(alert))

    if assigned_team is None:
        assigned_team = alert.get("assigned_team", assign_team(alert))

    resolved_at = now() if status == "Resolved" else None

    cursor.execute("""
    INSERT INTO agent_actions (
        created_at,
        risk_type,
        batch_id,
        client,
        product,
        severity,
        issue,
        recommended_action,
        assigned_team,
        status,
        priority_score,
        source_alert_id,
        due_date,
        resolved_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now(),
        alert.get("risk_type", ""),
        alert.get("batch_id", ""),
        alert.get("client", ""),
        alert.get("product", ""),
        alert.get("severity", ""),
        alert.get("issue", ""),
        alert.get("recommended_action", ""),
        assigned_team,
        status,
        priority_score,
        source_alert_id,
        due_date,
        resolved_at
    ))

    action_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return action_id


def load_agent_actions():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM agent_actions ORDER BY priority_score DESC, created_at DESC",
        conn
    )
    conn.close()
    return df


def update_action_status(action_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    resolved_at = now() if new_status == "Resolved" else None

    cursor.execute("""
    UPDATE agent_actions
    SET status = ?, resolved_at = ?
    WHERE id = ?
    """, (new_status, resolved_at, action_id))

    conn.commit()
    conn.close()


# -----------------------------
# AUTO ACTION CREATION
# -----------------------------
def save_alert_and_action(alert, status="Open", autonomous_mode=True):
    alert_id = save_alert(alert, status=status)

    action_id = None

    if autonomous_mode:
        action_id = save_agent_action(
            alert,
            assigned_team=assign_team(alert),
            status="Open",
            source_alert_id=alert_id
        )

    return alert_id, action_id


# -----------------------------
# AGENT LOG FUNCTIONS
# -----------------------------
def save_agent_log(log_type, message, user_email=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO agent_logs (
        created_at,
        log_type,
        message,
        user_email
    )
    VALUES (?, ?, ?, ?)
    """, (
        now(),
        log_type,
        message,
        user_email
    ))

    conn.commit()
    conn.close()


def load_agent_logs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM agent_logs ORDER BY created_at DESC", conn)
    conn.close()
    return df


# -----------------------------
# STREAMING SIMULATION FUNCTIONS
# -----------------------------
def save_stream_event(event_type, batch_id, severity, message, payload=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO stream_events (
        created_at,
        event_type,
        batch_id,
        severity,
        message,
        payload
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        now(),
        event_type,
        batch_id,
        severity,
        message,
        payload
    ))

    conn.commit()
    conn.close()


def load_stream_events(limit=50):
    conn = get_connection()
    df = pd.read_sql_query(
        f"SELECT * FROM stream_events ORDER BY created_at DESC LIMIT {int(limit)}",
        conn
    )
    conn.close()
    return df
