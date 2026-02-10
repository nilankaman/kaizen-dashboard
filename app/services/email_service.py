import smtplib
from email.message import EmailMessage

from app.core.config import settings


def _smtp_configured() -> bool:
    return bool(settings.smtp_host and settings.smtp_port and settings.from_email)


def send_invite_email(to_email: str, invite_link: str) -> None:
    """
    Send team invite link to email.
    In local/dev, if SMTP isn't configured, we just print the link (so dev flow still works).
    """
    subject = "You're invited to Kaizen Dashboard"
    body = (
        "Hello,\n\n"
        "You have been invited to join a team in Kaizen Dashboard.\n\n"
        f"Accept invite: {invite_link}\n\n"
        "If you didn't expect this invite, you can ignore this email.\n"
    )

    # Dev-friendly fallback
    if not _smtp_configured():
        print(f"[DEV EMAIL] To: {to_email}")
        print(f"[DEV EMAIL] Subject: {subject}")
        print(f"[DEV EMAIL] Link: {invite_link}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.from_email
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        # try TLS if possible
        try:
            server.starttls()
            server.ehlo()
        except Exception:
            pass

        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)

        server.send_message(msg)