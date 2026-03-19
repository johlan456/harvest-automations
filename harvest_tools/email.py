"""Shared email helper using Gmail SMTP with app password."""

import mimetypes
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(
    subject: str,
    body: str,
    html: str | None = None,
    recipient: str | None = None,
    attachments: list[str] | None = None,
) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_APP_PASSWORD"]
    if recipient is None:
        recipient = os.environ["EMAIL_RECIPIENT"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    for filepath in attachments or []:
        path = Path(filepath)
        mime_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        msg.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
