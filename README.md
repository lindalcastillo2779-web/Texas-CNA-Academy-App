# Texas CNA Academy – TULIP-Link Portal

TULIP-Link & CNA Academy is a mobile-friendly **Streamlit** application for Texas nurse aide
students, active CNAs, DONs, instructors, and healthcare facilities to manage exam prep,
renewal readiness, CEU tracking, and staffing compliance.

---

## Features

| Page | Description |
|------|-------------|
| 🏠 Home | Self-registration & sign-in |
| 📚 Exam Prep | NATCEP-aligned practice quizzes |
| 📋 CEU Tracker | Log & track continuing-education hours |
| ✅ Renewal Check | Renewal readiness dashboard with email reminders |
| 🏥 Staffing Log | Facility shift & compliance tracking |
| 🔧 Admin Panel | Admin-only management (users, questions, quiz log) |

---

## Local Development

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and edit secrets (never commit secrets.toml)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your SMTP and admin credentials

# 4. Run the app
streamlit run streamlit_app.py
```

The local SQLite database is stored at `data/cna_academy.db` (git-ignored).

---

## Deploying to Render

### 1. Push this repository to GitHub, then create a new **Web Service** on [Render](https://render.com).

The `render.yaml` in this repo is pre-configured:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
disk:
  name: cna-data
  mountPath: /data
  sizeGB: 1
```

### 2. Set environment variables in Render → Environment

| Key | Value |
|-----|-------|
| `STREAMLIT_SERVER_HEADLESS` | `true` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | your Gmail address |
| `SMTP_PASSWORD` | Gmail app password |
| `ADMIN_SECRET` | strong random string |

### 3. Connect the custom domain `texascnaacademyapp.com`

In **Render → Settings → Custom Domains**, add:
- `texascnaacademyapp.com`
- `www.texascnaacademyapp.com`

Then add these DNS records at your registrar (**Namecheap**):

| Type | Host | Value |
|------|------|-------|
| CNAME | `www` | `texas-cna-academy.onrender.com` |
| CNAME / ALIAS | `@` | `texas-cna-academy.onrender.com` |

> **Namecheap tip:** In the Advanced DNS tab, set the `@` record as an **ALIAS** (URL Redirect
> or CNAME Flattening) if your registrar supports it, or use an A-record pointing to Render's
> IP. `www` should always be a CNAME.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SMTP_HOST` | No* | SMTP server hostname |
| `SMTP_PORT` | No* | SMTP port (default: 587) |
| `SMTP_USER` | No* | SMTP username / email |
| `SMTP_PASSWORD` | No* | SMTP password or app password |
| `ADMIN_SECRET` | Yes | Password for the Admin Panel |

\* Email features are silently skipped when SMTP is not configured.

---

## Project Structure

```
streamlit_app.py          # Main entry-point & navigation
db.py                     # SQLite schema, init, and helper functions
auth.py                   # Admin authentication
email_utils.py            # SMTP email helpers
pages/
  home.py                 # Welcome / registration page
  exam_prep.py            # Practice quiz
  ceu_tracker.py          # CEU logging & progress
  renewal_check.py        # Renewal readiness dashboard
  staffing.py             # Staffing compliance log
  admin.py                # Admin panel
render.yaml               # Render deployment configuration
requirements.txt          # Python dependencies
.streamlit/
  config.toml             # Streamlit theme & server settings
  secrets.toml.example    # Template for local secrets
data/                     # Local dev SQLite database (git-ignored)
```
