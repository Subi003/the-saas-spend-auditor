from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .data import METRICS, SUBSCRIPTIONS
from .utils import format_inr


def build_audit_pdf(metrics: dict | None = None, subscriptions: list | None = None) -> bytes:
    metrics = metrics or METRICS
    subscriptions = subscriptions or SUBSCRIPTIONS
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=.55 * inch, leftMargin=.55 * inch, topMargin=.55 * inch, bottomMargin=.55 * inch)
    styles = getSampleStyleSheet()
    story = [Paragraph("The SaaS Spend Auditor", styles["Title"]), Paragraph(f"Executive audit report · {datetime.now():%B %d, %Y}", styles["Normal"]), Spacer(1, .25 * inch)]
    summary = [["Metric", "Value"]] + [[name, value] for name, value in metrics.items()]
    summary_table = Table(summary, colWidths=[3.7 * inch, 2 * inch])
    summary_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#071426")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#dbe3ec")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7fb")]), ("PADDING", (0, 0), (-1, -1), 8)]))
    story.extend([summary_table, Spacer(1, .3 * inch), Paragraph("Detected subscriptions", styles["Heading2"])])
    rows = [["Product", "Category", "Monthly", "Status", "Renewal"]]
    for item in subscriptions:
        product = item.product if hasattr(item, "product") else item["product"]
        category = item.category if hasattr(item, "category") else item["category"]
        cost = item.monthly_cost if hasattr(item, "monthly_cost") else item["monthly_cost"]
        status = item.status if hasattr(item, "status") else item["status"]
        renewal = item.renewal_days if hasattr(item, "renewal_days") else item.get("renewal_days")
        rows.append([product, category, format_inr(cost), status or "Unknown", f"{renewal} days" if renewal is not None else "Unknown"])
    table = Table(rows, repeatRows=1, colWidths=[1.8 * inch, 1.25 * inch, .9 * inch, .9 * inch, .8 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#071426")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#dbe3ec")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]), ("PADDING", (0, 0), (-1, -1), 6), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
    story.extend([table, Spacer(1, .25 * inch), Paragraph("Estimated annualized savings are based on detected opportunities.", styles["Heading2"])])
    document.build(story)
    return buffer.getvalue()
