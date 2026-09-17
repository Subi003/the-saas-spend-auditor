from __future__ import annotations

from numbers import Real


def format_inr(amount: float | int | None) -> str:
    """Format a number using Indian digit grouping, for example ₹1,23,456."""
    if amount is None:
        return "Unknown"
    value = float(amount)
    sign = "-" if value < 0 else ""
    absolute = abs(value)
    whole = int(absolute)
    decimal = round(absolute - whole, 2)
    grouped = str(whole)
    if len(grouped) > 3:
        last_three = grouped[-3:]
        remaining = grouped[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        grouped = ",".join(groups + [last_three])
    decimals = f"{decimal:.2f}"[1:] if decimal else ""
    return f"{sign}₹{grouped}{decimals}"


def numeric_value(value: object) -> float:
    """Convert currency-like values to a positive numeric spend amount."""
    if value is None:
        return 0.0
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"nan", "none", "null", "-"}:
        return 0.0
    negative = text.startswith("(") or text.startswith("-")
    cleaned = "".join(char for char in text if char.isdigit() or char == ".")
    try:
        amount = abs(float(cleaned))
    except ValueError:
        return 0.0
    return -amount if negative else amount
