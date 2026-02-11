from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PlanType(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONETIME = "onetime"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="user")
    payments: Mapped[list[Payment]] = relationship(back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_type: Mapped[PlanType] = mapped_column(SqlEnum(PlanType), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    access_key_encrypted: Mapped[str] = mapped_column(Text)
    reminder_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="subscriptions")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plan_type: Mapped[PlanType] = mapped_column(SqlEnum(PlanType), index=True)
    amount_rub: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(64))
    provider_charge_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(SqlEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="payments")
