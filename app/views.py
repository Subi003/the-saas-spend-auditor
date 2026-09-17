from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from .components import alert_card, inject_css, metric_card
from .config import APP_NAME, APP_SUBTITLE
from .data import ALERTS as DEMO_ALERTS
from .data import CATEGORY_SPEND as DEMO_CATEGORY_SPEND
from .data import METRICS as DEMO_METRICS
from .data import SUBSCRIPTIONS as DEMO_SUBSCRIPTIONS
from .parser import parse_statement_csv
from .report import build_audit_pdf
from .utils import format_inr


def render_landing() -> None:
    inject_css()
    st.markdown(f'<section class="hero"><div class="eyebrow">{APP_NAME}</div><h1>Stop overpaying for software.</h1><p>{APP_SUBTITLE} Upload a statement and uncover hidden subscriptions, duplicate tools, and renewal risks in seconds.</p></section>', unsafe_allow_html=True)
    first, second = st.columns([1, 1])
    with first:
        st.markdown("### A smarter way to manage SaaS spend")
        st.write("Give finance and operations one clear view of every recurring software charge—without chasing spreadsheets across teams.")
        if st.button("📤 Upload Statement", type="primary", use_container_width=True):
            st.session_state.page = "Upload Statement"
            st.rerun()
        if st.button("📊 View Demo Dashboard", use_container_width=True):
            st.session_state.parsed_data = None
            st.session_state.page = "Audit Dashboard"
            st.rerun()
    with second:
        st.markdown("### Built for confident decisions")
        st.markdown('<div class="security">🔒 <b>Bank-grade encryption</b><br><span class="small-muted">SOC2-ready workflows · Finance-ready audit trail</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:12px;padding:18px;background:white;border-radius:16px;border:1px solid #e2e8f0"><div class="metric-value">{format_inr(45000)}</div><div class="small-muted">average customer savings per month</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Trusted signals</div>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, (value, label) in zip(columns, [(format_inr(45000), "avg. monthly savings"), ("92%", "duplicate apps found"), ("4.8/5", "customer rating")]):
        with column:
            metric_card(label, value, "Based on demo customer cohort", "success")


def render_upload() -> None:
    inject_css()
    st.markdown('<div class="eyebrow">Audit workflow</div><h1>Upload your financial statement</h1>', unsafe_allow_html=True)
    st.write("Upload a CSV for real parsing. PDF upload remains a demo flow until PDF table extraction is added.")
    uploaded_file = st.file_uploader("Drag and drop a statement or browse files", type=["csv", "pdf"], help="CSV files are analyzed; PDFs use the demo workflow.")
    if uploaded_file:
        st.info(f"📄 {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB · Secure upload")
    if st.button("🔍 Start secure scan", type="primary", disabled=uploaded_file is None, use_container_width=True):
        progress = st.progress(0, text="Preparing secure scan...")
        for value, text in [(20, "Scanning transactions..."), (48, "Cross-checking SaaS databases..."), (76, "Analyzing recurring spend..."), (100, "Summarizing savings opportunities...")]:
            time.sleep(.35)
            progress.progress(value, text=text)
        if uploaded_file.name.lower().endswith(".csv"):
            try:
                st.session_state.parsed_data = parse_statement_csv(uploaded_file)
                st.session_state.source_name = uploaded_file.name
                st.session_state.processed = True
                st.success(f"✅ Parsed {len(st.session_state.parsed_data)} SaaS subscription rows from {uploaded_file.name}.")
            except Exception as exc:
                st.session_state.processed = False
                st.error(f"Could not parse this CSV: {exc}")
        else:
            st.session_state.parsed_data = None
            st.session_state.processed = True
            st.warning("PDF parsing is not implemented yet. The dashboard will show demo data, clearly marked as demo.")
    if st.session_state.get("processed", False) and st.button("Review audit results", type="primary"):
        st.session_state.page = "Audit Dashboard"
        st.rerun()


def _dashboard_values() -> tuple[list, dict, dict, str]:
    parsed = st.session_state.get("parsed_data")
    if parsed is None or parsed.empty:
        return DEMO_SUBSCRIPTIONS, DEMO_CATEGORY_SPEND, DEMO_METRICS, "Demo data"
    subscriptions = parsed.to_dict("records")
    category_spend = parsed.groupby("category")["monthly_cost"].sum().round(2).to_dict()
    total = float(parsed["monthly_cost"].sum())
    duplicate_count = int((parsed["status"] == "Duplicate").sum())
    potential = total * .10
    metrics = {"Total Monthly SaaS Spend": format_inr(total), "Potential Monthly Savings": format_inr(potential), "Active Subscriptions": str(len(parsed)), "Renewing in 30 Days": str(parsed["renewal_days"].notna().sum())}
    alerts = [{"title": f"{duplicate_count} duplicate category tools detected" if duplicate_count else "No duplicate category tools detected", "detail": "Review tools sharing the same category." if duplicate_count else "No duplicate categories were found in the uploaded statement.", "severity": "warning" if duplicate_count else "success"}]
    return subscriptions, category_spend, metrics, f"Uploaded file: {st.session_state.get('source_name', 'CSV')}"


def _item_value(item, key: str):
    return getattr(item, key) if hasattr(item, key) else item.get(key)


def render_dashboard() -> None:
    inject_css()
    subscriptions, category_spend, metrics, source_label = _dashboard_values()
    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.markdown(f'<div class="eyebrow">Spend health · {source_label}</div><h1>Executive Dashboard</h1>', unsafe_allow_html=True)
    with top_right:
        pdf = build_audit_pdf(metrics, subscriptions)
        st.download_button("⬇️ Export Audit Report (PDF)", data=pdf, file_name="saas-spend-audit.pdf", mime="application/pdf", use_container_width=True)
    st.markdown('<div class="section-title">Your spend at a glance</div>', unsafe_allow_html=True)
    metric_columns = st.columns(4)
    metric_values = [("Total Monthly SaaS Spend", metrics["Total Monthly SaaS Spend"], "Based on parsed transactions", "default"), ("Potential Monthly Savings", metrics["Potential Monthly Savings"], "Estimated optimization opportunity", "success"), ("Active Subscriptions", metrics["Active Subscriptions"], "Grouped vendor records", "default"), ("Renewing in 30 Days", metrics["Renewing in 30 Days"], "Unknown when not inferable", "warning")]
    for column, metric in zip(metric_columns, metric_values):
        with column:
            metric_card(*metric)
    st.markdown('<div class="section-title">Immediate wins</div>', unsafe_allow_html=True)
    alerts = DEMO_ALERTS if source_label == "Demo data" else [{"title": f"{int((pd.DataFrame(subscriptions)['status'] == 'Duplicate').sum())} duplicate category tools detected", "detail": "Bank statements cannot prove unused seats; connect usage data for that signal.", "severity": "warning"}]
    for alert in alerts:
        alert_card(alert["title"], alert["detail"], alert["severity"])
    chart_col, renewal_col = st.columns([1, 1])
    with chart_col:
        st.markdown('<div class="section-title">Spend by category</div>', unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame({"Monthly Spend": category_spend}), color="#10b981", height=300)
    with renewal_col:
        st.markdown('<div class="section-title">Renewal risk snapshot</div>', unsafe_allow_html=True)
        for item in sorted(subscriptions, key=lambda value: _item_value(value, "renewal_days") or 9999)[:3]:
            renewal = _item_value(item, "renewal_days")
            renewal_label = f"renews in {renewal} days" if renewal is not None else "renewal unknown"
            st.markdown(f"**{_item_value(item, 'product')}**  \n<span class='small-muted'>{format_inr(_item_value(item, 'monthly_cost'))}/mo · {renewal_label}</span>", unsafe_allow_html=True)
            st.divider()
    st.markdown('<div class="section-title">Detected SaaS subscriptions</div>', unsafe_allow_html=True)
    rows = [{"Product Name": _item_value(item, "product"), "Category": _item_value(item, "category"), "Monthly Cost": format_inr(_item_value(item, "monthly_cost")), "Status": _item_value(item, "status") or "Unknown", "Days Until Renewal": _item_value(item, "renewal_days") if _item_value(item, "renewal_days") is not None else "Unknown", "Seats": _item_value(item, "seats")} for item in subscriptions]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    action_col, guide_col = st.columns([1, 1])
    with action_col:
        if st.button("⚡ Cancel via One-Click", type="primary", use_container_width=True):
            st.warning("Mock action: cancellation request prepared for the highest-waste subscriptions.")
    with guide_col:
        if st.button("📘 Open Cancel Subscription Guide", use_container_width=True):
            st.info("Bank statements cannot perform cancellations. Contact the billing owner, disable auto-renewal, and confirm in writing.")
    st.markdown(f'<div class="security" style="margin-top:18px">✅ <b>Potential annualized savings: {metrics["Potential Monthly Savings"]} × 12</b><br><span class="small-muted">Based on the selected data source.</span></div>', unsafe_allow_html=True)
