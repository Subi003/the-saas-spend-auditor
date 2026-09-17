from __future__ import annotations

import streamlit as st

from .config import COLORS, STATUS_COLORS


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
            html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
            .stApp {{ background: #f4f7fb; }}
            [data-testid="stSidebar"] {{ background: {COLORS['navy']}; }}
            [data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}
            .hero {{ padding: 2.8rem 3rem; border-radius: 24px; background: linear-gradient(135deg, #071426 0%, #102a46 100%); color: white; margin-bottom: 1.25rem; }}
            .hero h1 {{ font-size: clamp(2.2rem, 5vw, 4.1rem); line-height: 1.05; letter-spacing: -0.06em; margin: 0.55rem 0 1rem; }}
            .hero p {{ color: #cbd5e1; font-size: 1.1rem; max-width: 680px; }}
            .eyebrow {{ color: #6ee7b7; font-size: 0.75rem; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; }}
            .metric {{ background: white; border: 1px solid #e2e8f0; border-radius: 18px; padding: 1.1rem; min-height: 125px; box-shadow: 0 5px 18px rgba(15,23,42,.04); }}
            .metric-label {{ color: #64748b; font-size: .83rem; }}
            .metric-value {{ color: #0f172a; font-size: 2rem; font-weight: 800; margin-top: .45rem; }}
            .metric-note {{ color: #64748b; font-size: .78rem; margin-top: .4rem; }}
            .section-title {{ color: #0f172a; font-size: 1.35rem; font-weight: 800; margin: 1.5rem 0 .7rem; }}
            .alert-card {{ border-radius: 16px; padding: 1rem 1.15rem; margin: .5rem 0; background: #fffbeb; border: 1px solid #fde68a; }}
            .alert-card.danger {{ background: #fff1f2; border-color: #fecdd3; }}
            .alert-title {{ color: #0f172a; font-weight: 700; }}
            .alert-detail {{ color: #475569; font-size: .87rem; margin-top: .3rem; }}
            .security {{ border-radius: 16px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 1rem 1.2rem; color: #065f46; }}
            .small-muted {{ color: #64748b; font-size: .85rem; }}
            div[data-testid="stFileUploader"] {{ background: white; border-radius: 18px; padding: 1rem; border: 2px dashed #cbd5e1; }}
            .stButton > button {{ border-radius: 10px; font-weight: 600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str, accent: str = "default") -> None:
    border = {"success": COLORS["emerald"], "warning": COLORS["amber"], "danger": COLORS["red"]}.get(accent, "#e2e8f0")
    st.markdown(
        f"""<div class="metric" style="border-top: 4px solid {border}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def alert_card(title: str, detail: str, severity: str = "warning") -> None:
    class_name = "alert-card danger" if severity == "danger" else "alert-card"
    icon = "🚨" if severity == "danger" else "⚠️"
    st.markdown(
        f"""<div class="{class_name}"><div class="alert-title">{icon} {title}</div><div class="alert-detail">{detail}</div></div>""",
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, COLORS["slate"])
    background = {"Active": "#ecfdf5", "Unused": "#fffbeb", "Duplicate": "#fff1f2"}.get(status, "#f1f5f9")
    return f'<span style="background:{background};color:{color};padding:4px 9px;border-radius:999px;font-size:.75rem;font-weight:700">{status}</span>'
