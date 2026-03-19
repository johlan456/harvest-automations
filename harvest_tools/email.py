"""Shared email helper using Gmail SMTP with app password."""

import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(subject: str, body: str, html: str | None = None) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_APP_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
