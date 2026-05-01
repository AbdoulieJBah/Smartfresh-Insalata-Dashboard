import os
import smtplib
import requests
from email.mime.text import MIMEText
import streamlit as st


def get_secret(key, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


def send_slack_alert(message):
    webhook_url = get_secret("SLACK_WEBHOOK_URL")

    if not webhook_url:
        return False, "Slack webhook not configured"

    try:
        response = requests.post(
            webhook_url,
            json={"text": message},
            timeout=10
        )

        if response.status_code == 200:
            return True, "Slack alert sent"

        return False, f"Slack failed: {response.status_code}"

    except Exception as e:
        return False, str(e)


def send_email_alert(subject, message):
    smtp_host = get_secret("SMTP_HOST")
    smtp_port = int(get_secret("SMTP_PORT", 587))
    smtp_user = get_secret("SMTP_USER")
    smtp_password = get_secret("SMTP_PASSWORD")
    email_to = get_secret("ALERT_EMAIL_TO")

    if not all([smtp_host, smtp_user, smtp_password, email_to]):
        return False, "Email settings not configured"

    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = email_to

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [email_to], msg.as_string())
        server.quit()

        return True, "Email alert sent"

    except Exception as e:
        return False, str(e)


def notify_critical_alert(alert):
    message = f"""
🚨 SmartFresh AI Critical Alert

Risk Type: {alert.get("risk_type")}
Batch: {alert.get("batch_id")}
Severity: {alert.get("severity")}
Priority: {alert.get("priority_score")}
Assigned Team: {alert.get("assigned_team")}
Issue: {alert.get("issue")}
Action: {alert.get("recommended_action")}
"""

    slack_ok, slack_msg = send_slack_alert(message)
    email_ok, email_msg = send_email_alert(
        subject=f"SmartFresh AI Alert: {alert.get('risk_type')}",
        message=message
    )

    return {
        "slack": slack_msg,
        "email": email_msg,
        "slack_ok": slack_ok,
        "email_ok": email_ok
    }
