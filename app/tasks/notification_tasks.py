import os
import json
import asyncio
import uuid
import aiosmtplib
from email.message import EmailMessage
from app.utils.celery_app import celery_app
from app.utils.cache import redis_client
from app.repositories.user_repository import UserRepository

CHANNEL = "notifications:job_events"
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


async def _send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        start_tls=True,
    )


async def _get_user_email(actor_id: str) -> str | None:
    from app.utils.database import AsyncSessionLocal
    from app.repositories.user_repository import UserRepository
    
    # Try cache first
    print("Before cache ")
    cached = await redis_client.get(f"rbac:permissions:{actor_id}")
    print("If the data is cahced ", cached)
    if cached:
        data = json.loads(cached)
        return data.get("email")
    
    # Fallback to DB
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        user = await repo.get_by_id(actor_id)
        print("After cache if user is present ", user)
        if user:
            return user.get("email")  # Fix dictionary dot-notation
    
    return None


async def _persist_notification(recipient_id: str, subject: str, body: str):
    from app.utils.database import AsyncSessionLocal
    from app.repositories.notification_repository import NotificationRepository
    from app.models.notification import Notification, NotificationState

    n = Notification(
        notification_id=str(uuid.uuid4()),
        recipient_id=recipient_id,
        subject=subject,
        body=body,
        state=NotificationState.sent,
    )
    async with AsyncSessionLocal() as db:
        repo = NotificationRepository(db)
        await repo.create(n)


@celery_app.task
def listen_job_events():
    async def _run():
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(CHANNEL)
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                print("Received message: ", message)
                event = json.loads(message["data"])
                actor_id = event.get("actor_id")
                subject = event.get("subject", "Notification")
                body = event.get("body", "")
                skip_persist = event.get("skip_persist", False)

                if not skip_persist:
                    await _persist_notification(actor_id, subject, body)
                    print(f"✅ Notification persisted for {actor_id}")

                email = await _get_user_email(actor_id)
                print("Email for actor_id {}: {}".format(actor_id, email))
                if email:
                    try:
                        await _send_email(email, subject, body)
                        print(f"📧 Email successfully sent to {email}")
                    except Exception as e:
                        print(f"❌ Error sending email: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⚠️ No email found for actor_id: {actor_id}")
            except Exception as e:
                print(f"❌ Error processing event: {e}")
                import traceback
                traceback.print_exc()

    asyncio.run(_run())
