from __future__ import annotations

from dataclasses import dataclass

from .utils import format_inr


@dataclass(frozen=True)
class Subscription:
    product: str
    category: str
    monthly_cost: float
    status: str
    renewal_days: int | None
    seats: int = 1


SUBSCRIPTIONS = [
    Subscription("Adobe Creative Cloud", "Productivity", 15000, "Active", 4, 12),
    Subscription("Figma", "Design", 18500, "Unused", 11, 9),
    Subscription("Slack Pro", "Collaboration", 8000, "Duplicate", 19, 35),
    Subscription("Notion", "Productivity", 8000, "Active", 28, 24),
    Subscription("HubSpot Marketing Hub", "Marketing", 28500, "Active", 21, 8),
    Subscription("Zoom Workplace", "Communication", 6250, "Unused", 8, 18),
    Subscription("GitHub Enterprise", "Dev Tools", 65000, "Active", 26, 42),
    Subscription("AWS", "Dev Tools", 205000, "Active", 17, 1),
    Subscription("Dropbox Business", "Productivity", 10000, "Active", 11, 28),
    Subscription("Sentry", "Dev Tools", 22000, "Active", 23, 12),
]

CATEGORY_SPEND = {"Dev Tools": 292000, "Marketing": 28500, "Productivity": 33000, "Design": 18500, "Communication": 8000}
METRICS = {
    "Total Monthly SaaS Spend": format_inr(sum(item.monthly_cost for item in SUBSCRIPTIONS)),
    "Potential Monthly Savings": format_inr(48200),
    "Active Subscriptions": "24",
    "Renewing in 30 Days": "7",
}
ALERTS = [
    {"title": f"Alert: 3 unused Figma seats detected", "detail": f"Estimated savings: {format_inr(10000)}/month.", "severity": "warning"},
    {"title": f"Warning: Adobe auto-renews in 4 days at {format_inr(15000)}/month", "detail": "Review the renewal before the billing date.", "severity": "danger"},
]
