from enum import Enum


class SalePlan(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONETIME_3 = "onetime_3"
    ONETIME_6 = "onetime_6"


PLAN_TO_DAYS = {
    SalePlan.MONTHLY: 30,
    SalePlan.YEARLY: 365,
    SalePlan.ONETIME_3: 90,
    SalePlan.ONETIME_6: 180,
}
