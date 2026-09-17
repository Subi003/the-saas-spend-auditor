import streamlit as st

from app.config import APP_NAME
from app.views import render_dashboard, render_landing, render_upload

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "page" not in st.session_state:
    st.session_state.page = "Overview"
if "processed" not in st.session_state:
    st.session_state.processed = False

with st.sidebar:
    st.markdown("## 📈 SaaS Spend Auditor")
    st.caption("Find waste. Protect your budget.")
    st.divider()

    page = st.radio(
        "Workspace",
        ["Overview", "Upload Statement", "Audit Dashboard"],
        index=["Overview", "Upload Statement", "Audit Dashboard"].index(st.session_state.page),
    )
    st.session_state.page = page

    st.divider()
    st.success("Secure workspace")
    st.caption("Demo mode · All data is simulated")

if st.session_state.page == "Overview":
    render_landing()
elif st.session_state.page == "Upload Statement":
    render_upload()
else:
    render_dashboard()
