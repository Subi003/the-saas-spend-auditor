from __future__ import annotations

import io
import re
from dataclasses import asdict
from typing import Any

import pandas as pd

from .data import Subscription


VENDOR_RULES: dict[str, tuple[str, str]] = {
    "adobe": ("Adobe Creative Cloud", "Productivity"),
    "figma": ("Figma", "Design"),
    "slack": ("Slack", "Collaboration"),
    "notion": ("Notion", "Productivity"),
    "hubspot": ("HubSpot", "Marketing"),
    "zoom": ("Zoom", "Communication"),
    "github": ("GitHub", "Dev Tools"),
    "amazon web services": ("AWS", "Dev Tools"),
    "aws": ("AWS", "Dev Tools"),
    "dropbox": ("Dropbox", "Productivity"),
    "sentry": ("Sentry", "Dev Tools"),
    "atlassian": ("Atlassian", "Dev Tools"),
    "microsoft 365": ("Microsoft 365", "Productivity"),
    "microsoft": ("Microsoft", "Productivity"),
    "google workspace": ("Google Workspace", "Productivity"),
    "canva": ("Canva", "Design"),
    "openai": ("OpenAI", "Dev Tools"),
}

DESCRIPTION_COLUMNS = ("description", "merchant", "vendor", "name", "payee", "memo", "details", "transaction description")
AMOUNT_COLUMNS = ("amount", "transaction amount", "debit", "charge", "value", "cost", "price")
DATE_COLUMNS = ("date", "transaction date", "posted date", "posting date")


def _find_column(columns: list[str], candidates: tuple[str, ...]) -> str | None:
    normalized = {str(column).strip().lower(): column for column in columns}
    for candidate in candidates:
        if candidate in normalized:
            return str(normalized[candidate])
    for column in columns:
        lowered = str(column).strip().lower()
        if any(candidate in lowered for candidate in candidates):
            return str(column)
    return None


def _parse_amount(value: Any) -> float:
    if pd.isna(value):
        return 0.0
    text = str(value).strip().replace(",", "")
    negative = text.startswith("(") and text.endswith(")")
    number = re.sub(r"[^0-9.\-]", "", text.strip("()"))
    try:
        amount = abs(float(number))
    except ValueError:
        return 0.0
    return -amount if negative else amount


def _read_csv(uploaded_file: Any) -> pd.DataFrame:
    uploaded_file.seek(0)
    raw = uploaded_file.getvalue()
    if not raw:
        raise ValueError("The uploaded CSV file is empty.")
    try:
        return pd.read_csv(io.BytesIO(raw))
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(raw), encoding="latin-1")


def _read_pdf(uploaded_file: Any) -> pd.DataFrame:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF support is unavailable. Add pypdf to requirements.txt and redeploy.") from exc

    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
    lines: list[str] = []
    for page in reader.pages:
        lines.extend((page.extract_text() or "").splitlines())

    records: list[dict[str, str]] = []
    pattern = re.compile(r"(?P<date>\d{1,4}[/-]\d{1,2}[/-]\d{1,4})?\s*(?P<description>.+?)\s+(?P<amount>\(?\$?\d[\d,]*(?:\.\d{2})?\)?)$")
    for line in lines:
        match = pattern.match(" ".join(line.split()))
        if match and match.group("description"):
            records.append(match.groupdict())
    if not records:
        raise ValueError("Could not find transaction rows in this PDF. Upload a text-based statement or CSV.")
    return pd.DataFrame(records)


def read_uploaded_statement(uploaded_file: Any) -> pd.DataFrame:
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return _read_csv(uploaded_file)
    if filename.endswith(".pdf"):
        return _read_pdf(uploaded_file)
    raise ValueError("Please upload a CSV or PDF statement.")


def analyze_statement(uploaded_file: Any) -> dict[str, Any]:
    frame = read_uploaded_statement(uploaded_file)
    if frame.empty:
        raise ValueError("The uploaded statement contains no transaction rows.")

    description_column = _find_column(list(frame.columns), DESCRIPTION_COLUMNS)
    amount_column = _find_column(list(frame.columns), AMOUNT_COLUMNS)
    date_column = _find_column(list(frame.columns), DATE_COLUMNS)
    if not description_column or not amount_column:
        raise ValueError("Could not detect description and amount columns. Use columns such as description and amount.")

    normalized = pd.DataFrame()
    normalized["date"] = frame[date_column].astype(str) if date_column else ""
    normalized["description"] = frame[description_column].fillna("").astype(str).str.strip()
    normalized["amount"] = frame[amount_column].map(_parse_amount)
    normalized = normalized[(normalized["description"] != "") & (normalized["amount"] > 0)].copy()
    if normalized.empty:
        raise ValueError("No positive transaction amounts were found in the uploaded statement.")

    def classify(description: str) -> tuple[str, str]:
        lowered = description.lower()
        for keyword, result in VENDOR_RULES.items():
            if keyword in lowered:
                return result
        return (description[:32] or "Unknown vendor", "Other")

    normalized[["product", "category"]] = normalized["description"].apply(lambda value: pd.Series(classify(value)))
    grouped = normalized.groupby(["product", "category"], as_index=False).agg(monthly_cost=("amount", "sum"), transactions=("amount", "size"))
    subscriptions: list[Subscription] = []
    for row in grouped.itertuples(index=False):
        subscriptions.append(Subscription(row.product, row.category, round(float(row.monthly_cost), 2), "Active", 30, int(row.transactions)))

    category_spend = normalized.groupby("category")["amount"].sum().round(2).to_dict()
    total = float(normalized["amount"].sum())
    potential = sum(item.monthly_cost for item in subscriptions if item.category == "Other") * 0.15
    potential += sum(item.monthly_cost for item in subscriptions if item.monthly_cost >= 100) * 0.08
    potential = round(potential, 2)
    renewal_count = sum(item.renewal_days <= 30 for item in subscriptions)
    alerts = []
    for item in sorted(subscriptions, key=lambda subscription: subscription.monthly_cost, reverse=True)[:2]:
        alerts.append({
            "title": f"Review {item.product} at ${item.monthly_cost:,.0f}/month",
            "detail": f"Detected from {item.seats} transaction(s) in your uploaded statement.",
            "severity": "warning" if item.monthly_cost < 250 else "danger",
        })

    return {
        "subscriptions": subscriptions,
        "category_spend": category_spend,
        "metrics": {
            "Total Monthly SaaS Spend": f"${total:,.0f}",
            "Potential Monthly Savings": f"${potential:,.0f}",
            "Active Subscriptions": str(len(subscriptions)),
            "Renewing in 30 Days": str(renewal_count),
        },
        "alerts": alerts,
        "transactions": normalized,
        "source_name": uploaded_file.name,
    }


def serializable_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    """Convert analysis to session-safe plain data when needed."""
    result = dict(analysis)
    result["subscriptions"] = [asdict(item) for item in analysis["subscriptions"]]
    result.pop("transactions", None)
    return result
