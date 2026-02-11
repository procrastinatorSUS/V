from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Payment, PaymentStatus, User

router = Router()
settings = get_settings()


@router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery, session: AsyncSession) -> None:
    if callback.from_user.id not in settings.admin_id_set:
        await callback.answer("Недостаточно прав", show_alert=True)
        return

    users_count = await session.scalar(select(func.count(User.id)))
    total_revenue = await session.scalar(
        select(func.coalesce(func.sum(Payment.amount_rub), 0)).where(Payment.status == PaymentStatus.PAID)
    )
    await callback.message.answer(
        "📊 Админ-панель\n"
        f"Пользователей: {users_count}\n"
        f"Доход: {total_revenue} RUB"
    )
    await callback.answer()
