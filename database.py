import sqlite3
import pandas as pd
from datetime import datetime
from database import save_alert, save_agent_log, load_alerts

DB_NAME = "smartfresh.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

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
        status TEXT
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
        status TEXT
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
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# ALERT FUNCTIONS
# -----------------------------
def save_alert(alert, status="Open"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO alerts (
        timestamp,
        risk_type,
        batch_id,
        severity,
        issue,
        recommended_action,
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        alert.get("risk_type", ""),
        alert.get("batch_id", ""),
        alert.get("severity", ""),
        alert.get("issue", ""),
        alert.get("recommended_action", ""),
        status
    ))

    conn.commit()
    conn.close()


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
def save_agent_action(alert, assigned_team="Operations Team", status="Open"):
    conn = get_connection()
    cursor = conn.cursor()

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
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        alert.get("risk_type", ""),
        alert.get("batch_id", ""),
        alert.get("client", ""),
        alert.get("product", ""),
        alert.get("severity", ""),
        alert.get("issue", ""),
        alert.get("recommended_action", ""),
        assigned_team,
        status
    ))

    conn.commit()
    conn.close()


def load_agent_actions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM agent_actions ORDER BY created_at DESC", conn)
    conn.close()
    return df


def update_action_status(action_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE agent_actions
    SET status = ?
    WHERE id = ?
    """, (new_status, action_id))

    conn.commit()
    conn.close()


# -----------------------------
# AGENT LOG FUNCTIONS
# -----------------------------
def save_agent_log(log_type, message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO agent_logs (
        created_at,
        log_type,
        message
    )
    VALUES (?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        log_type,
        message
    ))

    conn.commit()
    conn.close()


def load_agent_logs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM agent_logs ORDER BY created_at DESC", conn)
    conn.close()
    return df
