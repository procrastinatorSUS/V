from datetime import UTC, datetime, timedelta

from aiogram import Bot
from sqlalchemy import select

from app.db.models import Subscription
from app.db.session import SessionLocal


async def send_expiry_reminders(bot: Bot) -> None:
    now = datetime.now(UTC)
    threshold = now + timedelta(days=3)
    async with SessionLocal() as session:
        records = await session.scalars(
            select(Subscription).where(
                Subscription.is_active.is_(True),
                Subscription.ends_at <= threshold,
                Subscription.ends_at > now,
                Subscription.reminder_sent_at.is_(None),
            )
        )
        for sub in records:
            await bot.send_message(sub.user.telegram_id, "⚠️ Ваша подписка истечёт через 3 дня.")
            sub.reminder_sent_at = now
        await session.commit()
