from __future__ import annotations

import re
from typing import BinaryIO

import pandas as pd

from .utils import numeric_value

DESCRIPTION_NAMES = ("description", "merchant", "vendor", "payee", "name", "memo", "details", "transaction description")
AMOUNT_NAMES = ("amount", "transaction amount", "debit", "charge", "cost", "value", "price")
DATE_NAMES = ("date", "transaction date", "posted date", "posting date")
CATEGORY_NAMES = ("category", "type", "expense category", "merchant category")

KNOWN_VENDORS: list[tuple[str, str, str]] = [
    ("adobe", "Adobe Creative Cloud", "Productivity"),
    ("figma", "Figma", "Design"),
    ("slack", "Slack", "Collaboration"),
    ("notion", "Notion", "Productivity"),
    ("zoom", "Zoom", "Communication"),
    ("hubspot", "HubSpot", "Marketing"),
    ("github", "GitHub", "Dev Tools"),
    ("amazon web services", "AWS", "Dev Tools"),
    ("aws", "AWS", "Dev Tools"),
    ("dropbox", "Dropbox", "Productivity"),
    ("sentry", "Sentry", "Dev Tools"),
    ("atlassian", "Atlassian", "Dev Tools"),
    ("microsoft 365", "Microsoft 365", "Productivity"),
    ("google workspace", "Google Workspace", "Productivity"),
    ("canva", "Canva", "Design"),
    ("openai", "OpenAI", "Dev Tools"),
]


def _column(columns: list[object], names: tuple[str, ...]) -> object | None:
    normalized = {str(column).strip().lower(): column for column in columns}
    for name in names:
        if name in normalized:
            return normalized[name]
    for column in columns:
        label = str(column).strip().lower()
        if any(name in label for name in names):
            return column
    return None


def normalize_vendor(value: object) -> str:
    text = str(value).upper().strip()
    text = re.sub(r"\b(INC|INCORPORATED|LLC|LTD|LIMITED|PVT|PRIVATE|CORP|CORPORATION)\b", "", text)
    text = re.sub(r"[*#]+", " ", text)
    text = re.sub(r"\b(STORE|STR|POS)\s*\d+\b", "", text)
    text = re.sub(r"[^A-Z0-9& ]", " ", text)
    return re.sub(r"\s+", " ", text).strip().title()


def _known_vendor(description: str) -> tuple[str, str] | None:
    lowered = description.lower()
    for keyword, product, category in KNOWN_VENDORS:
        if keyword in lowered:
            return product, category
    return None


def parse_statement_csv(uploaded_file: BinaryIO) -> pd.DataFrame:
    """Parse a bank/card CSV into dashboard-compatible SaaS subscription rows."""
    uploaded_file.seek(0)
    frame = pd.read_csv(uploaded_file)
    if frame.empty:
        raise ValueError("The uploaded CSV is empty.")

    description_col = _column(list(frame.columns), DESCRIPTION_NAMES)
    amount_col = _column(list(frame.columns), AMOUNT_NAMES)
    date_col = _column(list(frame.columns), DATE_NAMES)
    category_col = _column(list(frame.columns), CATEGORY_NAMES)
    if description_col is None or amount_col is None:
        raise ValueError("Could not find description/merchant and amount/debit columns in the CSV.")

    clean = pd.DataFrame({
        "description": frame[description_col].fillna("").astype(str),
        "amount": frame[amount_col].map(numeric_value).abs(),
    })
    clean["date"] = pd.to_datetime(frame[date_col], errors="coerce") if date_col is not None else pd.NaT
    clean["source_category"] = frame[category_col].fillna("").astype(str) if category_col is not None else ""
    clean = clean[(clean["description"].str.strip() != "") & (clean["amount"] > 0)].copy()
    if clean.empty:
        raise ValueError("No positive transactions were found in the CSV.")

    classified = clean["description"].map(_known_vendor)
    clean["product"] = [match[0] if match else normalize_vendor(value) for value, match in zip(clean["description"], classified)]
    clean["category"] = [match[1] if match else (category if category and category.lower() != "nan" else "Other") for match, category in zip(classified, clean["source_category"])]
    clean["known"] = classified.notna()

    # A known SaaS vendor is included immediately. Unknown vendors are included only
    # when they recur, avoiding one-off grocery/travel transactions in the audit.
    counts = clean.groupby("product")["description"].transform("size")
    clean = clean[clean["known"] | (counts >= 2)].copy()
    if clean.empty:
        raise ValueError("No recurring SaaS/software transactions were detected in this CSV.")

    grouped = clean.groupby(["product", "category"], as_index=False).agg(monthly_cost=("amount", "sum"), seats=("amount", "size"))
    category_counts = grouped.groupby("category")["product"].transform("count")
    grouped["status"] = grouped.apply(lambda row: "Duplicate" if category_counts.loc[row.name] > 1 else "Unknown", axis=1)
    grouped["renewal_days"] = None
    return grouped[["product", "category", "monthly_cost", "status", "renewal_days", "seats"]]
