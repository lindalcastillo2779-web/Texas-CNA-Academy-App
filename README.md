# Texas CNA Academy – TULIP-Link Portal

Texas CNA Academy is a mobile-friendly training and resource platform for Texas nurse aide students, active CNAs, instructors, DONs, and healthcare facilities. This project supports exam preparation, renewal readiness, CEU tracking, staffing compliance, and access to important Texas CNA-related references and forms.

## What this project is about

This project is designed to support Texas nurse aide education, training readiness, and program organization. It brings together:

- exam-preparation tools for nurse aide students
- renewal and continuing education tracking support
- staffing and compliance support tools
- access to important Texas CNA and NATCEP-related forms and references
- a central location for curriculum, planning, and operational resources

The goal is to provide a practical, organized, and easy-to-use platform that supports both learning and program administration.

## How to use this project

You can use this project in several ways:

1. **Students** can use it to prepare for nurse aide exams and track progress.
2. **CNAs** can use it to monitor renewal readiness and CEU-related information.
3. **Instructors and program leaders** can use it to organize training support materials and documentation.
4. **Facilities and administrators** can use it to support staffing and compliance workflows.

### Typical uses

- sign in and access learning or tracking tools
- review exam-prep materials
- track CEUs and renewal-related progress
- manage staffing and compliance information
- reference Texas nurse aide documents and related materials

## Important resources

Key resources connected to this project may include:

- **Texas Health and Human Services (HHSC)**
- **Texas Workforce Commission (TWC)**
- **Prometric Nurse Aide resources**
- **TULIP**
- **Texas Nurse Aide Performance Record – Form 5497-NATCEP**
- **Texas NATCEP requirement mapping documents**
- **training program waiver and related planning resources**

## Local development

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

The local SQLite database is stored at `data/cna_academy.db` and is git-ignored.

## Deploying to Render

### 1. Push this repository to GitHub, then create a new **Web Service** on Render.

The `render.yaml` file in this repository is pre-configured for deployment.

### 2. Set environment variables in Render

Recommended environment variables:

- `STREAMLIT_SERVER_HEADLESS=true`
- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USER=your email`
- `SMTP_PASSWORD=your app password`
- `ADMIN_SECRET=strong random string`

### 3. Connect the custom domain

Configured domain:

- `texascnaacademyapp.com`
- `www.texascnaacademyapp.com`

## Environment variables reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SMTP_HOST` | No* | SMTP server hostname |
| `SMTP_PORT` | No* | SMTP port |
| `SMTP_USER` | No* | SMTP username / email |
| `SMTP_PASSWORD` | No* | SMTP password or app password |
| `ADMIN_SECRET` | Yes | Password for the Admin Panel |

\* Email features are skipped when SMTP is not configured.

## Project structure

```text
streamlit_app.py          # Main entry-point and navigation
db.py                     # SQLite schema, initialization, and helpers
auth.py                   # Admin authentication
email_utils.py            # SMTP email helpers
pages/
  home.py                 # Welcome and registration page
  exam_prep.py            # Practice quiz tools
  ceu_tracker.py          # CEU logging and progress
  renewal_check.py        # Renewal readiness dashboard
  staffing.py             # Staffing compliance log
  admin.py                # Admin panel
render.yaml               # Render deployment configuration
requirements.txt          # Python dependencies
.streamlit/
  config.toml             # Streamlit theme and server settings
  secrets.toml.example    # Template for local secrets
data/                     # Local development SQLite database
```
