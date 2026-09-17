from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import METRICS, SUBSCRIPTIONS


def build_audit_pdf() -> bytes:
    """Create a compact PDF report from the current demo audit data."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("The SaaS Spend Auditor", styles["Title"]),
        Paragraph(f"Executive audit report · {datetime.now():%B %d, %Y}", styles["Normal"]),
        Spacer(1, 0.25 * inch),
    ]

    summary = [["Metric", "Value"]] + [[name, value] for name, value in METRICS.items()]
    summary_table = Table(summary, colWidths=[3.7 * inch, 2.0 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#071426")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dbe3ec")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fb")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.extend([summary_table, Spacer(1, 0.3 * inch), Paragraph("Detected subscriptions", styles["Heading2"])])

    subscriptions = [["Product", "Category", "Monthly", "Status", "Renewal"]]
    for subscription in SUBSCRIPTIONS:
        subscriptions.append([
            subscription.product,
            subscription.category,
            f"${subscription.monthly_cost:,.0f}",
            subscription.status,
            f"{subscription.renewal_days} days",
        ])
    subscription_table = Table(subscriptions, repeatRows=1, colWidths=[1.8 * inch, 1.25 * inch, 0.8 * inch, 0.85 * inch, 0.8 * inch])
    subscription_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#071426")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dbe3ec")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(subscription_table)
    story.extend([Spacer(1, 0.25 * inch), Paragraph("Estimated annualized savings: $28,080", styles["Heading2"])])
    document.build(story)
    return buffer.getvalue()
