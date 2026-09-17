# The SaaS Spend Auditor — Streamlit edition

A production-style MVP for identifying wasted software spend from uploaded financial statements. The primary implementation is now Python + Streamlit and is split into reusable modules.

## Stack

- Python 3.10+
- Streamlit
- Pandas
- ReportLab for PDF audit exports

## Run locally

```bash
cd the-saas-spend-auditor
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open the URL shown in the terminal, usually http://localhost:8501.

## Pages and modules

- `streamlit_app.py` — application entry point and navigation
- `app/views.py` — landing, upload, and dashboard page views
- `app/components.py` — shared CSS, cards, alerts, and badges
- `app/config.py` — theme constants and application configuration
- `app/data.py` — realistic demo subscription data
- `app/report.py` — PDF generation helpers
- `requirements.txt` — Python dependencies

## MVP behavior

The file uploader accepts CSV/PDF files and runs a realistic simulated processing workflow. The dashboard presents mocked but realistic SaaS spend data, alerts, renewal risk, cancellation actions, and a downloadable PDF report. No uploaded data is sent to an external service.

The original Next.js implementation remains in the repository for reference; run the Streamlit version with the command above.
