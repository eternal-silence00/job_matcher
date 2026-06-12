from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_jobs(email: str, jobs: list):
    
    body = "Hi! Here are new matching jobs for you:\n\n"
    for job in jobs:
        body += f"• {job.title} at {job.company}\n  {job.url}\n\n"

    message = MessageSchema(
        subject="New matching jobs",
        recipients=[email],
        body=body,
        subtype="plain"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)