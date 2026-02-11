CREATE TYPE plan_type AS ENUM ('monthly', 'yearly', 'onetime');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'canceled');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type plan_type NOT NULL,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    access_key_encrypted TEXT NOT NULL,
    reminder_sent_at TIMESTAMPTZ
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_ends_at ON subscriptions(ends_at);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type plan_type NOT NULL,
    amount_rub INTEGER NOT NULL CHECK (amount_rub > 0),
    provider VARCHAR(64) NOT NULL,
    provider_charge_id VARCHAR(255),
    status payment_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
