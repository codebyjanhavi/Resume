# SkillSight AI — System Architecture

## Overview

SkillSight AI is a local resume analysis application. A React single-page frontend sends requests to a Flask REST API. The backend parses uploaded resumes, extracts skills, predicts a likely job role, calculates compatibility with a target role, stores results in SQLite, and generates downloadable reports.

```text
Browser
  React + TypeScript + Vite
  Tailwind CSS + Recharts
       │ HTTP / JSON and multipart resume upload
       ▼
Flask API (/api/v1)
  ├── Resume parsing and section detection
  ├── Skill extraction and normalization
  ├── Job-role classifier and text similarity
  ├── Deterministic skill matching and recommendations
  ├── PDF / JSON report generation
  └── SQLAlchemy
       │
       ├── SQLite: resumes, skills, roles, analyses, roadmaps
       ├── Synthetic CSVs: seed role and skill reference data
       └── Joblib artifacts: classifier and TF-IDF vectorizer
```

## Frontend

- **Application:** React 19, TypeScript, Vite 8, React Router.
- **Styling:** Tailwind CSS; the interface uses a violet brand palette and a dark navy-to-purple sidebar.
- **Charts:** Recharts renders dashboard skill-gap visualizations.
- **HTTP client:** Axios communicates with the backend using the configured API base URL.
- **Current navigation:** Overview, Analyze Resume, Analysis History, and Reports. Analysis result details are opened from dashboard/history links. Role comparison and roadmap features have backend endpoints, but no dedicated frontend pages.

## Backend

- **Application:** Python and Flask, constructed through an application factory in `backend/app/__init__.py`.
- **API:** Flask blueprint mounted at `/api/v1`.
- **CORS:** Flask-CORS allows origins listed by `CORS_ORIGINS`; the example configuration lists localhost port 5173.
- **Persistence:** Flask-SQLAlchemy/SQLAlchemy with SQLite by default. The app creates tables and seeds the role/skill reference data when the database has not yet been seeded.
- **Uploads:** Resume files are temporarily written to the configured upload directory while parsing. Temporary files are cleaned up when configured; extracted resume data is persisted in the database.
- **Reports:** ReportLab creates PDF reports; the API also returns a JSON report.

## Resume and analysis flow

1. The frontend uploads a PDF, DOCX, or TXT resume.
2. `document_parser.py` extracts text and heuristically identifies contact information and common sections. Scanned PDFs do not undergo OCR.
3. `skill_extractor.py` finds canonical skill names and aliases using boundary-aware regular expressions.
4. The user can review and edit extracted skills in the frontend before submitting analysis.
5. The backend predicts a role with the trained classifier, calculates TF-IDF cosine similarity to the target description, and deterministically compares confirmed skills with mandatory/preferred requirements.
6. The backend stores analysis results and generates roadmap recommendations based on missing skills.
7. The frontend displays analysis details; PDF and JSON reports can be downloaded.

## Machine learning and matching components

- **Role prediction:** `CalibratedClassifierCV` around `LinearSVC`, using a saved TF-IDF vectorizer.
- **Text similarity:** TF-IDF and cosine similarity, computed between the resume and target job description.
- **Skill coverage:** Deterministic weighted comparison of confirmed skills and role requirements. This is not a trained ML model.
- **Skill extraction:** Alias-aware regex matching. This is not a trained ML model.
- **Roadmap recommendations:** Deterministic priority rules and curated resource suggestions based on missing requirements.

See [ml_methodology.md](./ml_methodology.md) for details.

## Main source directories

- `backend/app/api/` — HTTP endpoints.
- `backend/app/ml/` — loads saved classifier artifacts and predicts roles.
- `backend/app/models/` — SQLAlchemy database tables and relationships.
- `backend/app/services/` — resume parsing, skill extraction, matching, database seeding, and PDF creation.
- `backend/data/synthetic/` — synthetic benchmark CSVs and dataset metadata.
- `backend/artifacts/` — trained classifier, vectorizer, and evaluation metrics.
- `backend/scripts/` — optional data generation, model training, and evaluation programs; none is needed during ordinary app startup when included assets are present.
- `frontend/src/` — routes, pages, shared components, API client, types, and styles.

## Privacy and operational notes

The app does not call a paid AI API. Uploaded resume content and extracted personal details are stored in the local SQLite database until deleted. The frontend loads Google Fonts, and some curated learning resources link to external websites. The Flask development server is intended for local development, not production deployment.
