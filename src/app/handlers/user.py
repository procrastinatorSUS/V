from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import Payment, PaymentStatus, PlanType, Subscription, User
from app.keyboards.common import main_menu, plans_menu
from app.payments.plans import PLAN_TO_DAYS, SalePlan
from app.services.pricing import PricingPolicy
from app.services.security import encrypt_value

router = Router()
settings = get_settings()
pricing = PricingPolicy(settings.base_monthly_price, settings.yearly_discount_percent)


@router.message(CommandStart())
async def start(message: Message, session: AsyncSession, cipher) -> None:
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    if not user:
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        session.add(user)
        await session.commit()
    keyboard = main_menu(message.from_user.id in settings.admin_id_set)
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "buy")
async def buy_menu(callback: CallbackQuery) -> None:
    await callback.message.answer("Выберите тариф:", reply_markup=plans_menu().as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("plan:"))
async def create_invoice(callback: CallbackQuery, session: AsyncSession) -> None:
    plan = SalePlan(callback.data.split(":")[1])
    amount = {
        SalePlan.MONTHLY: pricing.monthly(),
        SalePlan.YEARLY: pricing.yearly(),
        SalePlan.ONETIME_3: pricing.onetime(3),
        SalePlan.ONETIME_6: pricing.onetime(6),
    }[plan]

    user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
    payment = Payment(
        user_id=user.id,
        plan_type=PlanType.YEARLY if plan == SalePlan.YEARLY else PlanType.MONTHLY,
        amount_rub=amount,
        provider="telegram_stars",
        status=PaymentStatus.PENDING,
    )
    session.add(payment)
    await session.flush()

    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Доступ к VLESS",
        description=f"План {plan.value}",
        payload=f"payment:{payment.id}:{plan.value}",
        provider_token=settings.provider_token.get_secret_value(),
        currency="RUB",
        prices=[LabeledPrice(label="VPN access", amount=amount * 100)],
    )
    await session.commit()
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout(pre_checkout_q: PreCheckoutQuery) -> None:
    await pre_checkout_q.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, session: AsyncSession, panel_client, cipher) -> None:
    payload = message.successful_payment.invoice_payload
    payment_id = int(payload.split(":")[1])
    plan = SalePlan(payload.split(":")[2])

    payment = await session.get(Payment, payment_id)
    user = await session.scalar(select(User).where(User.telegram_id == message.from_user.id))
    payment.status = PaymentStatus.PAID
    payment.provider_charge_id = message.successful_payment.telegram_payment_charge_id

    days = PLAN_TO_DAYS[plan]
    raw_key = await panel_client.issue_vless_key(days=days, user_tag=f"tg-{user.telegram_id}")
    subscription = Subscription(
        user_id=user.id,
        plan_type=PlanType.YEARLY if plan == SalePlan.YEARLY else PlanType.ONETIME,
        starts_at=datetime.now(UTC),
        ends_at=datetime.now(UTC) + timedelta(days=days),
        is_active=True,
        access_key_encrypted=encrypt_value(cipher, raw_key),
    )
    session.add(subscription)
    await session.commit()

    await message.answer("Оплата получена ✅ Доступ активирован.")


@router.callback_query(F.data == "my_key")
async def my_key(callback: CallbackQuery, session: AsyncSession, cipher) -> None:
    user = await session.scalar(select(User).where(User.telegram_id == callback.from_user.id))
    subscription = await session.scalar(
        select(Subscription)
        .where(Subscription.user_id == user.id, Subscription.is_active.is_(True))
        .order_by(Subscription.ends_at.desc())
    )
    if not subscription:
        await callback.message.answer("Активной подписки нет.")
    else:
        await callback.message.answer(
            f"Ваш ключ (зашифрован в БД): `{subscription.access_key_encrypted}`\n"
            f"Действует до: {subscription.ends_at:%Y-%m-%d}",
            parse_mode="Markdown",
        )
    await callback.answer()
