import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings
from app.handlers import admin, user
from app.middlewares.services import ServicesMiddleware
from app.services.reminder import send_expiry_reminders


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()

    services = ServicesMiddleware()
    dp.update.middleware.register(services)
    dp.include_router(user.router)
    dp.include_router(admin.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_expiry_reminders, "interval", hours=24, kwargs={"bot": bot})
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
