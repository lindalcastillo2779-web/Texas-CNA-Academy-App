# Texas CNA Academy 

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

\* Email features are skipped when SMTP is not configured.

## Project structure

```text
streamlit_app.py          # Main entry-point and navigation
db.py                     # SQLite schema, initialization, and helpers
auth.py                   # Admin authentication
email_utils.py            # SMTP email helpers
llm_client.py             # LLM provider adapter (OpenAI / Azure OpenAI)
buddy_service.py          # Buddy chatbot logic and RAG pipeline
knowledge_loader.py       # Document ingestion, chunking, and FAISS indexing
pages/
  home.py                 # Welcome and registration page
  courses.py              # NATCEP course roadmap and curriculum browser
  exam_prep.py            # Practice quiz tools
  ceu_tracker.py          # CEU logging and progress
  renewal_check.py        # Renewal readiness dashboard
  staffing.py             # Staffing compliance log
  buddy.py                # Buddy AI chatbot page
  admin.py                # Admin panel
knowledge/
  curriculum/             # Curriculum docs (.md / .txt / .pdf)
  media/                  # Central media registry for Streamlit pages and lessons
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
- `ceu_tracker`
- `renewal_check`
- `staffing`
- `buddy`
- `admin`

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

```
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
