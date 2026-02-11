from app.services.pricing import PricingPolicy


def test_yearly_discount() -> None:
    policy = PricingPolicy(monthly_price=500, yearly_discount_percent=20)
    assert policy.yearly() == 4800


def test_onetime_discount_6_months() -> None:
    policy = PricingPolicy(monthly_price=500, yearly_discount_percent=20)
    assert policy.onetime(6) == 2700
