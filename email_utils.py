"""Email utility for Texas CNA Academy – reads config from env vars or secrets.toml."""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st

APP_URL = "https://texascnaacademyapp.com"

def smtp_config() -> dict:
    """Return SMTP settings; Render env vars take priority over secrets.toml."""
    def _secret(*keys, default=""):
        try:
            obj = st.secrets
            for k in keys:
                obj = obj.get(k, {})
            return obj if isinstance(obj, (str, int)) else default
        except Exception:
            return default

    return {
        "host":     os.environ.get("SMTP_HOST") or _secret("smtp", "host"),
        "port":     int(os.environ.get("SMTP_PORT") or _secret("smtp", "port") or 587),
        "user":     os.environ.get("SMTP_USER") or _secret("smtp", "user"),
        "password": os.environ.get("SMTP_PASSWORD") or _secret("smtp", "password"),
    }


def send_email(to_address: str, subject: str, body_html: str) -> bool:
    """
    Send an HTML email.  Returns True on success, False on failure.
    Silently no-ops (returns True) when SMTP is not configured so the app
    remains usable without email credentials.
    """
    cfg = smtp_config()
    if not cfg["host"] or not cfg["user"] or not cfg["password"]:
        return True  # SMTP not configured – skip silently

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["user"]
    msg["To"] = to_address
    msg.attach(MIMEText(body_html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(cfg["user"], cfg["password"])
            server.sendmail(cfg["user"], to_address, msg.as_string())
        return True
    except Exception:
        return False


def send_welcome_email(name: str, to_address: str) -> bool:
    subject = "Welcome to Texas CNA Academy!"
    body = f"""
    <html><body>
    <h2>Welcome, {name}!</h2>
    <p>Thank you for joining the <strong>Texas CNA Academy</strong> (TULIP-Link) portal.</p>
    <p>You can now access exam prep, track your CEUs, and manage your renewal readiness.</p>
    <p>Questions? Reply to this email or visit
       <a href="{APP_URL}">{APP_URL}</a>.</p>
    <p>— Texas CNA Academy Team</p>
    </body></html>
    """
    return send_email(to_address, subject, body)


def send_ceu_reminder(name: str, to_address: str, hours_remaining: float) -> bool:
    subject = "Texas CNA Academy – CEU Reminder"
    body = f"""
    <html><body>
    <h2>CEU Reminder, {name}</h2>
    <p>You still need <strong>{hours_remaining:.1f} CEU hours</strong> to meet your renewal requirement.</p>
    <p>Log in to <a href="{APP_URL}">{APP_URL}</a> to log completed courses.</p>
    <p>— Texas CNA Academy Team</p>
    </body></html>
    """
    return send_email(to_address, subject, body)
