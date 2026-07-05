import logging
import os
import smtplib
from email.message import EmailMessage

import httpx

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("ALERT_EMAIL_TO"))


def _twilio_configured() -> bool:
    required = (
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "ALERT_SMS_TO",
    )
    return all(os.getenv(key) for key in required)


def send_email_alert(subject: str, body: str) -> bool:
    if not _smtp_configured():
        return False

    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM") or user
    recipients = [
        addr.strip()
        for addr in os.getenv("ALERT_EMAIL_TO", "").split(",")
        if addr.strip()
    ]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            if os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}:
                smtp.starttls()
                smtp.ehlo()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(message)
        logger.info("Email alert sent to %s", recipients)
        return True
    except Exception:
        logger.exception("Failed to send email alert")
        return False


def send_sms_alert(body: str) -> bool:
    if not _twilio_configured():
        return False

    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "")
    to_number = os.getenv("ALERT_SMS_TO", "")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    try:
        response = httpx.post(
            url,
            data={"From": from_number, "To": to_number, "Body": body[:1500]},
            auth=(account_sid, auth_token),
            timeout=30,
        )
        response.raise_for_status()
        logger.info("SMS alert sent to %s", to_number)
        return True
    except Exception:
        logger.exception("Failed to send SMS alert")
        return False


def dispatch_match_alerts(message: str) -> dict:
    """Send configured external alerts for a new match."""
    subject = "Bike Wishlist Match Found"
    sms_body = message if len(message) <= 1500 else message[:1497] + "..."

    return {
        "email_sent": send_email_alert(subject, message),
        "sms_sent": send_sms_alert(sms_body),
    }


def alerts_configured() -> dict:
    return {
        "email": _smtp_configured(),
        "sms": _twilio_configured(),
    }
