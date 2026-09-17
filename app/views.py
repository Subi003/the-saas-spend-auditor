from __future__ import annotations

import time

import pandas as pd
import streamlit as st

from .components import alert_card, inject_css, metric_card, status_badge
from .config import ALERTS, APP_NAME, APP_SUBTITLE, CATEGORY_SPEND, METRICS, SUBSCRIPTIONS
from .data import build_audit_pdf


def render_landing() -> None:
    inject_css()
    st.markdown(
        f"""<section class="hero"><div class="eyebrow">{APP_NAME}</div>
        <h1>Stop overpaying for software.</h1>
        <p>{APP_SUBTITLE} Upload a statement and uncover hidden subscriptions, duplicate tools, and renewal risks in seconds.</p></section>""",
        unsafe_allow_html=True,
    )

    first, second = st.columns([1, 1])
    with first:
        st.markdown("### A smarter way to manage SaaS spend")
        st.write("Give finance and operations one clear view of every recurring software charge—without chasing spreadsheets across teams.")
        if st.button("📤 Upload Statement", type="primary", use_container_width=True):
            st.session_state.page = "Upload Statement"
            st.rerun()
        if st.button("📊 View Demo Dashboard", use_container_width=True):
            st.session_state.page = "Audit Dashboard"
            st.rerun()
    with second:
        st.markdown("### Built for confident decisions")
        st.markdown("""<div class="security">🔒 <b>Bank-grade encryption</b><br><span class="small-muted">SOC2-ready workflows · Finance-ready audit trail</span></div>""", unsafe_allow_html=True)
        st.markdown("""<div style="margin-top:12px;padding:18px;background:white;border-radius:16px;border:1px solid #e2e8f0"><div class="metric-value">$540</div><div class="small-muted">average customer savings per month</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Trusted signals</div>', unsafe_allow_html=True)
    columns = st.columns(3)
    for column, (value, label) in zip(columns, [("$540", "avg. monthly savings"), ("92%", "duplicate apps found"), ("4.8/5", "customer rating")]):
        with column:
            metric_card(label, value, "Based on demo customer cohort", "success")


def render_upload() -> None:
    inject_css()
    st.markdown('<div class="eyebrow">Audit workflow</div><h1>Upload your financial statement</h1>', unsafe_allow_html=True)
    st.write("Accepts CSV or PDF exports from banks and credit cards. This MVP uses simulated processing and realistic demo results.")

    uploaded_file = st.file_uploader("Drag and drop a statement or browse files", type=["csv", "pdf"], help="CSV and PDF files are supported.")
    if uploaded_file:
        st.info(f"📄 {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB · Secure upload")

    if st.button("🔍 Start secure scan", type="primary", disabled=uploaded_file is None, use_container_width=True):
        progress = st.progress(0, text="Preparing secure scan...")
        stages = [
            (20, "Scanning transactions..."),
            (48, "Cross-checking SaaS databases..."),
            (76, "Analyzing usage patterns..."),
            (100, "Summarizing savings opportunities..."),
        ]
        for value, text in stages:
            time.sleep(0.55)
            progress.progress(value, text=text)
        st.session_state.processed = True

    if st.session_state.processed:
        st.success("✅ Statement analyzed successfully. We found 24 active subscriptions and 7 high-priority opportunities.")
        if st.button("Review audit results", type="primary"):
            st.session_state.page = "Audit Dashboard"
            st.rerun()


def render_dashboard() -> None:
    inject_css()
    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.markdown('<div class="eyebrow">Spend health</div><h1>Executive Dashboard</h1>', unsafe_allow_html=True)
    with top_right:
        pdf = build_audit_pdf()
        st.download_button("⬇️ Export Audit Report (PDF)", data=pdf, file_name="saas-spend-audit.pdf", mime="application/pdf", use_container_width=True)

    st.markdown('<div class="section-title">Your spend at a glance</div>', unsafe_allow_html=True)
    metric_columns = st.columns(4)
    metric_values = [
        ("Total Monthly SaaS Spend", METRICS["Total Monthly SaaS Spend"], "+4.2% vs last month", "default"),
        ("Potential Monthly Savings", METRICS["Potential Monthly Savings"], "Recoverable after optimization", "success"),
        ("Active Subscriptions", METRICS["Active Subscriptions"], "3 duplicate tools flagged", "default"),
        ("Renewing in 30 Days", METRICS["Renewing in 30 Days"], "2 critical renewals", "warning"),
    ]
    for column, metric in zip(metric_columns, metric_values):
        with column:
            metric_card(*metric)

    st.markdown('<div class="section-title">Immediate wins</div>', unsafe_allow_html=True)
    for alert in ALERTS:
        alert_card(alert["title"], alert["detail"], alert["severity"])

    chart_col, renewal_col = st.columns([1, 1])
    with chart_col:
        st.markdown('<div class="section-title">Spend by category</div>', unsafe_allow_html=True)
        category_df = pd.DataFrame({"Category": list(CATEGORY_SPEND.keys()), "Monthly Spend": list(CATEGORY_SPEND.values())}).set_index("Category")
        st.bar_chart(category_df, color="#10b981", height=300)
    with renewal_col:
        st.markdown('<div class="section-title">Renewal risk snapshot</div>', unsafe_allow_html=True)
        for subscription in sorted(SUBSCRIPTIONS, key=lambda item: item.renewal_days)[:3]:
            st.markdown(
                f"**{subscription.product}**  \n<span class='small-muted'>${subscription.monthly_cost:,.0f}/mo · renews in {subscription.renewal_days} days</span>",
                unsafe_allow_html=True,
            )
            st.divider()

    st.markdown('<div class="section-title">Detected SaaS subscriptions</div>', unsafe_allow_html=True)
    rows = []
    for subscription in SUBSCRIPTIONS:
        rows.append({
            "Product Name": subscription.product,
            "Category": subscription.category,
            "Monthly Cost": f"${subscription.monthly_cost:,.0f}",
            "Status": subscription.status,
            "Days Until Renewal": subscription.renewal_days,
            "Seats": subscription.seats,
        })
    table_df = pd.DataFrame(rows)
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status"),
            "Days Until Renewal": st.column_config.NumberColumn(format="%d days"),
        },
    )

    action_col, guide_col = st.columns([1, 1])
    with action_col:
        if st.button("⚡ Cancel via One-Click", type="primary", use_container_width=True):
            st.warning("Mock action: cancellation request prepared for the highest-waste subscriptions.")
    with guide_col:
        if st.button("📘 Open Cancel Subscription Guide", use_container_width=True):
            st.info("Mock guide: contact the billing owner, export usage evidence, disable auto-renewal, and confirm the cancellation in writing.")

    st.markdown("""<div class="security" style="margin-top:18px">✅ <b>Potential annualized savings: $28,080</b><br><span class="small-muted">Based on current usage and upcoming renewal windows.</span></div>""", unsafe_allow_html=True)
