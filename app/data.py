from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Subscription:
    product: str
    category: str
    monthly_cost: float
    status: str
    renewal_days: int
    seats: int = 1


SUBSCRIPTIONS = [
    Subscription("Adobe Creative Cloud", "Productivity", 180, "Active", 4, 12),
    Subscription("Figma", "Design", 220, "Unused", 11, 9),
    Subscription("Slack Pro", "Collaboration", 95, "Duplicate", 19, 35),
    Subscription("Notion", "Productivity", 96, "Active", 28, 24),
    Subscription("HubSpot Marketing Hub", "Marketing", 340, "Active", 21, 8),
    Subscription("Zoom Workplace", "Communication", 75, "Unused", 8, 18),
    Subscription("GitHub Enterprise", "Dev Tools", 780, "Active", 26, 42),
    Subscription("AWS", "Dev Tools", 2_450, "Active", 17, 1),
    Subscription("Dropbox Business", "Productivity", 120, "Active", 11, 28),
    Subscription("Sentry", "Dev Tools", 260, "Active", 23, 12),
]

CATEGORY_SPEND = {
    "Dev Tools": 4610,
    "Marketing": 3840,
    "Productivity": 2270,
    "Security": 1750,
}

METRICS = {
    "Total Monthly SaaS Spend": "$12,470",
    "Potential Monthly Savings": "$2,340",
    "Active Subscriptions": "24",
    "Renewing in 30 Days": "7",
}

ALERTS = [
    {
        "title": "Alert: 3 unused Figma seats detected",
        "detail": "9 seats are active, but 3 have no recent usage. Estimated savings: $120/mo.",
        "severity": "warning",
    },
    {
        "title": "Warning: Adobe auto-renews in 4 days at $120/mo",
        "detail": "Usage dropped 42% in the last 30 days. Review before renewal.",
        "severity": "danger",
    },
]
