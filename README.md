# Texas CNA Academy 

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink?logo=github-sponsors)](https://github.com/sponsors/lindalcastillo2779-web)

Texas CNA Academy is a mobile-friendly training and resource platform for Texas nurse aide students, active CNAs, instructors, DONs, and healthcare facilities. This project supports exam preparation, renewal readiness, CEU tracking, staffing compliance, access to important Texas CNA-related references and forms, and Texas-focused compliance-support workflows. [code_file:3][code_file:148]

Texas CNA Academy is an independent education and compliance-support platform. It is not operated by Texas Health and Human Services Commission (HHSC), TULIP, SEMARC, Prometric, the Nurse Aide Registry, or the Texas Board of Nursing, and official determinations remain the responsibility of the appropriate agencies and systems. [code_file:147][web:52][web:138]

## What this project is about

This project is designed to support Texas nurse aide education, training readiness, program organization, and selected compliance-awareness workflows. It brings together:

- exam-preparation tools for nurse aide students
- **interactive Clinical Skills Lab** for hands-on skill simulation (Prometric/NATCEP-aligned)
- **Community Mentor + Workforce Hub** for mentoring, study circles, practice partners, and local opportunities
- renewal and continuing education tracking support
- staffing and compliance support tools
- compliance guidance and regulatory update monitoring
- role-based workflow dashboards for students, instructors, DONs, and administrators
- instructor SEMARC workflow training and acknowledgment support
- access to important Texas CNA and NATCEP-related forms and references
- a central location for curriculum, planning, operational, and workflow-support resources

The goal is to provide a practical, organized, and easy-to-use platform that supports both learning and program administration. Recent revisions also add built-in compliance guidance, a regulatory updates monitor, Form 5497 and Form 5498 workflow support, and modular Streamlit page architecture for easier maintenance. [code_file:3][code_file:148][code_file:150][code_file:151][code_file:152]

## Clinical Skills Lab

The ** Clinical Skills Lab** is an interactive, Prometric- and NATCEP-aligned simulation section where CNA students can practice and self-assess the hands-on skills evaluated on the Texas CNA skills examination.

### Overview

Each scenario walks you through a skill using the same checklist format examiners use at Prometric testing centers. Decision points mirror real exam choices, and scoring reflects actual exam criteria.

### How to use Coach vs Exam mode

| Mode | Best used for | Hints | Feedback timing |
|------|---------------|-------|-----------------|
| **Coach Mode** | First-time practice, learning rationale | Full hints + rationale | Immediate after every step |
| **Exam Mode** | Self-assessment, exam-readiness check | None — mirrors real exam | Summary only after completion |

**Recommended workflow:**
1. Run each scenario in **Coach Mode** first to understand the correct sequence and rationale.
2. Once comfortable, switch to **Exam Mode** to test yourself under exam-like conditions.
3. Review the results summary for targeted remediation recommendations.

### What the scores mean

| Score | Weight | Meaning |
|-------|--------|---------|
| Checklist Score | 40 % | Percentage of non-critical technique steps answered correctly |
| Critical-Step Score | 40 % | Percentage of critical steps passed — **must be 100 %** (any miss = automatic Prometric failure) |
| Communication Score | 20 % | Communication and professionalism checkpoint completion |
| Overall Score | — | Weighted composite of all three components |

**Passing:** Overall ≥ 75 % AND all critical steps correct.

### Available scenarios

| Scenario | Key skills covered | Prometric skill |
|----------|--------------------|-----------------|
| Hand Hygiene & PPE | Hand-washing technique, donning/doffing sequence | Handwashing |
| Transfer: Bed ↔ Wheelchair | Environment prep, gait belt, brakes, body mechanics | Transfer from Bed to Wheelchair |
| Vital Signs & Documentation | Temp, pulse, respirations, BP, normal ranges, reporting | Measuring and Recording Vital Signs |

### Where to add new scenarios

1. Create a new JSON file under `knowledge/lab_scenarios/` following the structure of an existing scenario (e.g., `hand_hygiene_ppe.json`). Required fields: `id`, `title`, `description`, `natcep_domains`, `steps` (with `decision_points`), `communication_checkpoints`, `remediation_refs`.
2. Register the new file in `utils/lab_engine.py` by adding an entry to the `_SCENARIO_FILES` dictionary.
3. Add the step mappings to `knowledge/lab_scenarios/curriculum_mapping.json` under `scenario_mappings`.

## How to use this project

You can use this project in several ways:

1. **Students** can use it to prepare for nurse aide exams and track progress.
2. **CNAs** can use it to monitor renewal readiness and CEU-related information.
3. **Instructors and program leaders** can use it to organize training support materials, study groups, mentoring, compliance reminders, and internal workflow support.
4. **Facilities and administrators** can use it to support staffing, workforce outreach, regulatory update review, staff workflow tracking, and compliance workflows. [code_file:148][code_file:150][code_file:151][code_file:152]

### Typical uses

- sign in and access learning or tracking tools
- review exam-prep materials
- connect with mentors, practice partners, and local workforce opportunities
- track CEUs and renewal-related progress
- manage staffing and compliance information
- review regulatory update logs and workflow notices
- use role-based dashboards and training workflow pages
- reference Texas nurse aide documents and related materials

## Important resources

Key resources connected to this project may include:

- **Texas Health and Human Services (HHSC)**
- **Texas Workforce Commission (TWC)**
- **Prometric Nurse Aide resources**
- **TULIP**
- **SEMARC**
- **Texas Nurse Aide Performance Record – Form 5497-NATCEP**
- **Texas Nurse Aide Daily Sign-In Sheet – Form 5498-NATCEP**
- **Texas NATCEP requirement mapping documents**
- **training program waiver and related planning resources**
- **official provider letters and training notices related to NAR and SEMARC employability workflows** [web:59][web:138]

## New compliance and workflow pages

The revised app now includes additional built-in pages and tools to support Texas-specific program organization and workflow awareness:

- **Compliance Guidance** – Texas-focused reminders for renewal, NATCEP records, and employability-related workflow boundaries. [code_file:148]
- **Regulatory Updates Monitor** – Tracks selected official-source items, review dates, and internal action reminders. [code_file:150]
- **Role Workflows & Dashboards** – Provides role-specific views for Student, Instructor, DON, and Admin users, including Form 5497 and Form 5498 workflow support. [code_file:151]
- **Instructor SEMARC Training** – Provides internal training content, a short quiz, confidentiality reminders, and acknowledgment checkboxes for staff-facing SEMARC workflow education. [code_file:152]

These additions are intended to support internal organization and awareness. They do not replace official HHSC, TULIP, NAR, SEMARC, or Prometric processes. [code_file:147][web:52][web:131][web:59]

## Local development

```bash
# 1. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
npm ci

# 3. Copy and edit secrets (never commit secrets.toml)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your SMTP and admin credentials

# 4. Build the portal frontend
npm run build

# 5. Run the unified server (serves the portal API/static site and proxies Streamlit under /app)
python -m uvicorn app_server:app --host 0.0.0.0 --port 8000 --proxy-headers
```

The local SQLite database is stored at `data/cna_academy.db` and is git-ignored.

## Deploying to Render

### 1. Push this repository to GitHub, then create a new **Web Service** on Render.

The `render.yaml` file in this repository is pre-configured for deployment.

### 2. Set environment variables in Render

Recommended environment variables:

- `STREAMLIT_SERVER_HEADLESS=true`
- `STREAMLIT_INTERNAL_PORT=8501`
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
| `OPENAI_API_KEY` | Yes (OpenAI) | OpenAI API key for Buddy |
| `OPENAI_MODEL` | No | Chat model name (default: `gpt-4o-mini`) |
| `OPENAI_EMBEDDING_MODEL` | No | Embedding model for RAG (default: `text-embedding-3-small`) |
| `LLM_PROVIDER` | No | `OPENAI` (default) or `AZURE_OPENAI` |
| `AZURE_OPENAI_KEY` | Yes (Azure) | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Yes (Azure) | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Yes (Azure) | Azure chat deployment name |
| `AZURE_OPENAI_API_VERSION` | No | Azure API version (default: `2024-02-01`) |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | No | Azure embedding deployment name |
| `SMTP_HOST` | No* | SMTP server hostname |
| `SMTP_PORT` | No* | SMTP port |
| `SMTP_USER` | No* | SMTP username / email |
| `SMTP_PASSWORD` | No* | SMTP password or app password |
| `ADMIN_SECRET` | Yes | Password for the Admin Panel |
| `STREAMLIT_INTERNAL_PORT` | No | Internal child-process port used by the ASGI server to proxy Streamlit (default: `8501`) |
| `STRIPE_WEBHOOK_SECRET` | Yes (Stripe) | Stripe webhook signing secret used by `/api/billing/stripe/webhook` |
| `STRIPE_CORE_PRICE_IDS` | No | Comma-separated Stripe Price IDs that map to the `core` entitlement tier |
| `STRIPE_PRO_PRICE_IDS` | No | Comma-separated Stripe Price IDs that map to the `pro` entitlement tier |
| `STRIPE_WEBHOOK_TOLERANCE_SECONDS` | No | Max age for Stripe webhook signatures in seconds (default: `300`) |

\* Email features are skipped when SMTP is not configured.

## Project structure

```text
streamlit_app.py          # Main entry-point and navigation
app_utils.py              # Shared footer/disclaimer helpers for modular pages
db.py                     # SQLite schema, initialization, and helpers
auth.py                   # Admin authentication
email_utils.py            # SMTP email helpers
llm_client.py             # LLM provider adapter (OpenAI / Azure OpenAI)
buddy_service.py          # Buddy chatbot logic and RAG pipeline
knowledge_loader.py       # Document ingestion, chunking, and FAISS indexing
pages/
  home.py                 # Welcome and registration page
  compliance.py           # Texas-focused compliance guidance
  regulatory_updates.py   # Regulatory updates monitor
  role_dashboards.py      # Role-based dashboards + Form 5497/5498 workflow support
  semarc_training.py      # Instructor SEMARC training module and SOP acknowledgment support
  courses.py              # NATCEP course roadmap and curriculum browser
  exam_prep.py            # Practice quiz tools
  clinical_skills_lab.py  # Clinical Skills Lab – interactive CNA skill simulations
  community_hub.py        # Mentor matching, community board, and workforce opportunities
  ceu_tracker.py          # CEU logging and progress
  renewal_check.py        # Renewal readiness dashboard
  staffing.py             # Staffing compliance log
  buddy.py                # Buddy AI chatbot page
  admin.py                # Admin panel + community moderation
knowledge/
  curriculum/             # Curriculum docs (.md / .txt / .pdf)
  media/                  # Central media registry for Streamlit pages and lessons
  lab_scenarios/          # Clinical Skills Lab scenario definitions
    hand_hygiene_ppe.json               # Hand Hygiene & PPE scenario
    transfer_bed_wheelchair.json        # Transfer: Bed ↔ Wheelchair scenario
    vital_signs_documentation.json      # Vital Signs & Documentation scenario
    curriculum_mapping.json             # NATCEP/Prometric standards mapping
  tulip/                  # TULIP guidance docs
  twc/                    # TWC workforce docs
  texas_hhs/              # Texas HHSC/HHS regulatory docs
assets/
  images/
    pages/                # Page hero artwork and thumbnails
    lessons/              # Module-level visuals and placeholders
  video/                  # Optional local MP4/WebM clips
utils/
  media.py                # Safe registry loading, frontmatter parsing, and rendering helpers
  lab_engine.py           # Clinical Skills Lab engine: scenario loading, scoring, feedback
render.yaml               # Render deployment configuration
requirements.txt          # Python dependencies
.env.example              # Environment variable template
.streamlit/
  config.toml             # Streamlit theme and server settings
  secrets.toml.example    # Template for local secrets
data/                     # Local development SQLite database and Buddy index
```

## Media architecture

The Streamlit app now uses a shared media system so every page and curriculum lesson can
show a consistent hero visual and an optional video slot without hardcoding asset paths in
each page module.

- `knowledge/media/media_registry.json` is the central registry for page keys and module IDs.
- `utils/media.py` safely loads the registry, resolves local assets or HTTPS URLs, parses
  simple markdown frontmatter, and renders media with Streamlit-native `st.image()` and
  `st.video()` calls.
- `pages/*.py` call `render_page_media(...)` at the top of each page.
- `pages/courses.py` reads curriculum markdown with optional frontmatter and calls
  `render_module_media(...)` before showing lesson content.

If a media entry is missing, invalid, or unreadable, the app shows a friendly placeholder
message instead of crashing.

## Adding page or lesson media

### 1. Add assets

Place optimized files in one of these folders:

- `assets/images/pages/`
- `assets/images/lessons/`
- `assets/video/`

Relative paths in the registry or lesson frontmatter should be written from the repository
root, for example:

- `assets/images/pages/home-hero.webp`
- `assets/images/lessons/module_04_resident_rights.png`
- `assets/video/module_04_intro.mp4`

### 2. Register page media

Add or update an entry in `knowledge/media/media_registry.json`:

```json
"pages": {
  "home": {
    "hero_image": "assets/images/pages/home-hero.webp",
    "thumbnail": "assets/images/pages/home-thumb.webp",
    "video_url": "assets/video/home-intro.mp4",
    "caption": "Short welcome visual",
    "credit": "Photo or design credit",
    "source": "Owned asset or licensed source",
    "video_caption": "Optional intro video caption"
  }
}
```

Available page keys in the current Streamlit app are:

- `home`
- `courses`
- `exam_prep`
- `clinical_skills_lab`
- `ceu_tracker`
- `renewal_check`
- `staffing`
- `buddy`
- `admin`
- `compliance`
- `regulatory_updates`
- `role_dashboards`
- `semarc_training`

### 3. Register module media

Each curriculum markdown file is matched by its module ID, usually the file stem such as
`module_01_role_and_scope`.

You can define lesson media in either location:

1. `knowledge/media/media_registry.json`
2. Markdown frontmatter at the top of the lesson file

Example frontmatter:

```md
---
module_id: module_04_resident_rights
title: Module 04: Residents' Rights
hero_image: assets/images/lessons/module_04_resident_rights.webp
thumbnail: assets/images/lessons/module_04_resident_rights-thumb.webp
video_url: assets/video/module_04_resident_rights.mp4
caption: Lesson banner for rights and dignity topics.
credit: Texas CNA Academy
source: Licensed or owned media
video_caption: 90-second rights overview clip.
---
```

Frontmatter is optional. Existing markdown lessons continue to work without it.

## Recommended media specs and optimization tips

- **Page hero images:** target about `1600 x 900`
- **Lesson hero images:** target about `1200 x 675`
- **Preferred image formats:** WebP or optimized PNG/SVG
- **Short lesson videos:** 30–120 seconds when possible
- **Local video formats:** MP4 (H.264) or WebM for best compatibility
- **Performance tips:**
  - keep hero images compressed before committing
  - avoid very large local videos in Streamlit Cloud
  - prefer short clips or external HTTPS-hosted video when appropriate
  - use the registry defaults so missing media still has a graceful fallback

## Buddy chatbot setup

Buddy is a role-aware AI study and compliance assistant powered by OpenAI (or Azure OpenAI).

### 1. Set API credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Then edit .env:
# OPENAI_API_KEY=sk-...your-key-here...
```

Load the `.env` file before running the app:

```bash
# Linux/macOS
export $(grep -v '^#' .env | xargs)
streamlit run streamlit_app.py

# Or use python-dotenv by adding `from dotenv import load_dotenv; load_dotenv()` at the top of streamlit_app.py
```

### 2. (Optional) Switch to Azure OpenAI

Set these variables instead:

```bash
LLM_PROVIDER=AZURE_OPENAI
AZURE_OPENAI_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01
```

No code changes are required — Buddy switches providers automatically.

### 3. Build the knowledge index (RAG)

Add your documents (`.md`, `.txt`, or `.pdf`) to the appropriate subfolders under `knowledge/`:

```text
knowledge/curriculum/   ← NATCEP curriculum docs
knowledge/tulip/        ← TULIP guidance
knowledge/twc/          ← TWC workforce resources
knowledge/texas_hhs/    ← Texas HHSC/HHS regulatory docs
```

Then run the ingestion script:

```bash
python knowledge_loader.py
```

This builds a FAISS vector index under `data/`. Buddy will automatically use retrieved
snippets to ground its answers. If no index exists, Buddy still works using the LLM's
general training data and will display a notice.

### 4. Render deployment

Add the following to your Render environment variables:

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | `OPENAI` or `AZURE_OPENAI` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_MODEL` | Model name (default: `gpt-4o-mini`) |

Azure variables (`AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`) are only needed when `LLM_PROVIDER=AZURE_OPENAI`.

## Sponsoring this project

Texas CNA Academy is an open-source project. Everything here — study materials, skill checklists, curriculum templates, exam-prep tools, and compliance workflows — is free to use, share, and build on.

If this project saves you time, helps your students pass their exam, or makes your program run smoother, please consider supporting its continued development.

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink?logo=github-sponsors&style=for-the-badge)](https://github.com/sponsors/lindalcastillo2779-web)

### What your support funds

- New NATCEP curriculum modules and study materials
- Skill simulation scenario development (Clinical Skills Lab)
- Maintenance, bug fixes, and security updates
- Hosting and infrastructure costs
- Community features: mentor matching, workforce hub, peer study circles
- Compliance-support workflows, regulatory monitoring, and instructor training tools

### How to sponsor

GitHub Sponsors supports both **monthly** and **one-time** contributions — individuals and organizations are both welcome.

1. Click the **Sponsor** button at the top of this repository page, or visit [github.com/sponsors/lindalcastillo2779-web](https://github.com/sponsors/lindalcastillo2779-web).
2. Choose a tier (or enter a custom amount for a one-time gift).
3. Complete checkout through GitHub — payments are processed securely by GitHub/Stripe.

All sponsors are recognized in the GitHub Sponsors section of this repository. Corporate sponsors interested in a higher-visibility acknowledgment are welcome to open a discussion.

## Code-Along Educational Package

A sellable code-along package scaffold now exists in `./educational-package/` with:

- product scope and audience definition
- free-vs-paid access tiers
- onboarding and progression path (`START_HERE.md`)
- standardized module templates + MVP module (M01)
- tutorials/study-guides/templates/sample-data/instructor-notes structure
- legal, support, release, feedback, and trust-signal documentation

Start with `./educational-package/START_HERE.md`.









 



  
