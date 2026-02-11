from dataclasses import dataclass


@dataclass(slots=True)
class PricingPolicy:
    monthly_price: int
    yearly_discount_percent: int

    def monthly(self) -> int:
        return self.monthly_price

    def yearly(self) -> int:
        full_price = self.monthly_price * 12
        discount = full_price * self.yearly_discount_percent // 100
        return full_price - discount

    def onetime(self, months: int) -> int:
        if months < 1:
            raise ValueError("months must be >= 1")
        if months >= 6:
            discount_percent = 10
        elif months >= 3:
            discount_percent = 5
        else:
            discount_percent = 0
        full_price = self.monthly_price * months
        return full_price - (full_price * discount_percent // 100)
