# SkillSight AI — Resume Skill Gap Analyzer

SkillSight AI is a local web application for parsing resumes, extracting skills, predicting likely technical job roles, and comparing candidate skills with a target role. It provides a dashboard, analysis history, and downloadable PDF/JSON analysis reports.

The project uses a synthetic dataset to train and evaluate its job-role classifier. The tool is intended for career exploration and self-assessment, not for automated hiring decisions.

## Contents

- [Features](#features)
- [Technology](#technology)
- [Run the application](#run-the-application)
- [Optional data and model generation](#optional-data-and-model-generation)
- [Using the application](#using-the-application)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Data, models, and storage](#data-models-and-storage)
- [Configuration](#configuration)
- [Tests and quality checks](#tests-and-quality-checks)
- [Privacy and limitations](#privacy-and-limitations)
- [Additional documentation](#additional-documentation)
- [License](#license)

## Features

- Upload PDF, DOCX, or TXT resumes and extract text locally.
- Parse contact details and infer common resume sections.
- Identify skills with boundary-aware phrase matching and aliases, such as `k8s` → `Kubernetes`.
- Review detected skills and add or remove skills before analysis.
- Predict a likely job role and show alternative role predictions.
- Compare a resume against a predefined role or a pasted job description.
- Calculate mandatory and overall weighted skill coverage, and show matched, missing, and additional skills.
- Compare the resume's text with the target description using TF-IDF and cosine similarity.
- Generate heuristic resume-improvement suggestions.
- Create a prioritized learning roadmap with suggested projects and curated learning resources. The backend/API supports roadmaps; there is currently no dedicated roadmap page in the frontend.
- View dashboard metrics, analysis history, and analysis reports.
- Download analysis reports as PDF or JSON.

The current frontend navigation contains **Overview**, **Analyze Resume**, **Analysis History**, and **Reports**. Analysis results open from the dashboard or history. Other backend API capabilities (such as role comparison and roadmap retrieval) remain available through the API even though there is no dedicated frontend page for them.

## Technology

| Area | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite 8, React Router, Tailwind CSS, Recharts, Lucide React, Axios |
| Backend | Python 3.11+, Flask, Flask-CORS, Flask-SQLAlchemy, SQLAlchemy |
| Resume processing | PyMuPDF, python-docx |
| Machine learning and data | scikit-learn, pandas, NumPy, joblib |
| Reports | ReportLab |
| Database | SQLite |
| Tests | pytest; Oxlint for frontend linting |

Use a Node.js release supported by the installed Vite 8 version (Node 20.19+ or 22.12+ recommended), plus npm.

## Run the application

Run the backend and frontend in **two separate PowerShell terminals**. Commands below assume you are in the project root.

### 1. Backend

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap"
.\venv\Scripts\python.exe backend\run.py
```

The backend listens at `http://127.0.0.1:5000`. Its API base path is `http://127.0.0.1:5000/api/v1`.

If the virtual environment does not exist yet, create it and install the backend dependencies:

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap"
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Python 3.11 or later is required; Python 3.13 is used in the existing environment.

### 2. Frontend

Open a second terminal:

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap\frontend"
npm install
npm run dev
```

Vite prints the frontend URL when it starts, usually `http://localhost:5173/`. If that port is occupied, Vite may choose another port. The backend's `CORS_ORIGINS` setting must include the frontend origin if it uses a different port.

Do not open the backend root URL expecting the website: the frontend is the user interface. To check the backend, open `http://127.0.0.1:5000/api/v1/health`.

## Optional data and model generation

The generated CSV files and trained model artifacts are already included in the project. **You do not need to regenerate them to run the application.**

### Regenerate the synthetic datasets (optional)

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap"
.\venv\Scripts\python.exe backend\scripts\generate_synthetic_data.py
```

This reproducibility utility writes synthetic benchmark data to `backend/data/synthetic/`. It is not run during normal application startup.

### Retrain the job-role classifier (optional)

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap"
.\venv\Scripts\python.exe backend\scripts\train_models.py
```

Training reads `synthetic_resumes.csv`, performs a stratified 80/20 split and five-fold cross-validation for candidate comparison, then saves the selected calibrated LinearSVC model, its TF-IDF vectorizer, and evaluation metrics under `backend/artifacts/`. Run the dataset generator first only if the required CSV files are missing or you intentionally want to recreate the data.

To evaluate saved artifacts on a synthetic sample:

```powershell
.\venv\Scripts\python.exe backend\scripts\evaluate_models.py
```

## Using the application

1. Open the frontend URL printed by Vite.
2. Go to **Analyze Resume** and upload a `.pdf`, `.docx`, or `.txt` file.
3. Review extracted skills; edit the list if needed.
4. Choose a target job role or provide a custom job description.
5. Run the analysis.
6. Review the predicted role, skill coverage, text similarity, skills breakdown, and resume suggestions.
7. Open **Analysis History** or **Reports** to revisit results and download reports.

The role classifier predicts one of these 15 roles:

1. Data Scientist
2. Machine Learning Engineer
3. Data Analyst
4. Python Developer
5. Full Stack Developer
6. Frontend Developer
7. Backend Developer
8. Java Developer
9. DevOps Engineer
10. Cloud Engineer
11. Cybersecurity Analyst
12. Business Analyst
13. Software Engineer
14. AI Engineer
15. Database Administrator

## API reference

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Backend and model status |
| `GET` | `/roles` | Predefined roles and their requirements |
| `GET` | `/skills` | Skill catalog |
| `POST` | `/resumes` | Upload and parse a resume (`file` multipart field) |
| `GET` | `/resumes/{resume_id}` | Get a resume and its extracted skills |
| `DELETE` | `/resumes/{resume_id}` | Delete a resume |
| `PUT` | `/resumes/{resume_id}/skills` | Replace the resume's confirmed skills |
| `POST` | `/analysis` | Run an analysis |
| `GET` | `/analysis?page=1&per_page=10` | Get paginated analysis history |
| `GET` | `/analysis/{analysis_id}` | Get one analysis |
| `DELETE` | `/analysis/{analysis_id}` | Delete an analysis |
| `POST` | `/roles/compare` | Compare a resume against multiple role IDs |
| `GET` | `/roadmaps/{analysis_id}` | Get the roadmap generated for an analysis |
| `PATCH` | `/roadmaps/{roadmap_id}/items/{item_id}` | Update a roadmap item's status |
| `GET` | `/metrics/dashboard` | Get database-backed dashboard statistics |
| `GET` | `/models/metrics` | Get saved classifier evaluation metrics |
| `GET` | `/reports/{analysis_id}/pdf` | Download a PDF report |
| `GET` | `/reports/{analysis_id}/json` | Download an analysis JSON report |

An analysis request accepts `resume_id` and may include `target_role_id`, `custom_job_description`, and `confirmed_skills`. See [docs/api.md](./docs/api.md) for additional details.

## Project structure

```text
Resume_Skill_Gap/
├── README.md
├── docs/                         # Architecture, API, dataset, ML, and usage docs
├── backend/
│   ├── .env.example              # Example backend configuration
│   ├── requirements.txt          # Python dependencies
│   ├── run.py                    # Flask development entry point
│   ├── skillsight.db             # Local SQLite database
│   ├── app/
│   │   ├── __init__.py           # Flask app factory and database initialization
│   │   ├── config.py             # Backend configuration
│   │   ├── extensions.py         # SQLAlchemy and CORS instances
│   │   ├── api/routes.py         # Versioned REST API
│   │   ├── ml/predictor.py       # Loads model artifacts and predicts roles
│   │   ├── models/models.py      # SQLAlchemy database models
│   │   ├── models/__init__.py    # Re-exports model classes
│   │   └── services/
│   │       ├── db_seeder.py      # Seeds roles and skills from CSV files
│   │       ├── document_parser.py # Extracts text, contacts, and resume sections
│   │       ├── matching_engine.py # Similarity, skill coverage, and recommendations
│   │       ├── pdf_report_generator.py # Creates analysis PDF reports
│   │       └── skill_extractor.py # Finds and normalizes skills
│   ├── artifacts/                # Trained model, vectorizer, and metrics
│   ├── data/synthetic/           # Synthetic CSV datasets and metadata
│   ├── scripts/
│   │   ├── generate_synthetic_data.py # Optional reproducible dataset generator
│   │   ├── train_models.py       # Optional classifier training pipeline
│   │   └── evaluate_models.py    # Optional saved-model evaluation
│   ├── tests/                    # Backend pytest tests
│   └── uploads/                  # Temporary uploaded resume files
└── frontend/
    ├── .env.example              # Example API URL
    ├── package.json              # Frontend dependencies and commands
    ├── index.html
    └── src/
        ├── App.tsx               # Frontend routes
        ├── pages/                # Overview, analyze, results, history, reports
        ├── components/           # Header, sidebar, skill badge, skill review modal
        ├── layouts/              # Dashboard page shell
        ├── services/api.ts       # HTTP client for the backend
        ├── types/                # Shared TypeScript data types
        └── index.css             # Global styles
```

The `docs/` directory contains `architecture.md`, `api.md`, `ml_methodology.md`, `dataset.md`, and `user_guide.md`.

Python may create `__pycache__` folders while running. They contain disposable bytecode caches, not project source or model data.

## Data, models, and storage

### Synthetic data

All benchmark/training records are fictional and generated locally. The fixed seed is `42`. The included data consists of:

- `synthetic_resumes.csv` — 5,250 synthetic resume profiles (350 per role), used to train/evaluate the role classifier.
- `synthetic_job_descriptions.csv` — 1,200 synthetic job descriptions (80 per role).
- `role_skill_requirements.csv` — mandatory and preferred skills and weights for the supported roles.
- `skills_taxonomy.csv` — canonical skill names, categories, aliases, and default weights, used when seeding the database.
- `synthetic_dataset_metadata.json` — dataset summary and file manifest.

### Classifier and analysis methods

- **Job-role prediction:** a `CalibratedClassifierCV` wrapping `LinearSVC`, using a TF-IDF vectorizer. Logistic Regression is trained/evaluated as a comparison candidate; the saved prediction model is the calibrated LinearSVC.
- **Resume-to-description similarity:** TF-IDF features and cosine similarity. This is lexical text similarity, not a measure of hiring suitability.
- **Skill compatibility:** deterministic weighted matching of candidate skills against role requirements. It is not a trained model.
- **Skill extraction:** boundary-aware regular-expression matching against canonical skill names and aliases.
- **Learning recommendations:** deterministic priority and resource recommendations based on missing mandatory/preferred skills.

The current `backend/artifacts/metrics.json` contains evaluation results recorded by training. The included synthetic data yields a reported 100% held-out score; this should **not** be interpreted as evidence of 100% accuracy on real-world resumes.

### Persistent and temporary files

- `backend/skillsight.db` stores parsed resume records, extracted skills, roles, analyses, roadmaps, and progress.
- Uploaded documents are temporarily written to `backend/uploads/` for text extraction. Temporary files are configured to be cleaned up after processing; parsed resume text and related data are retained in SQLite.
- `backend/artifacts/job_role_classifier.joblib` is the trained classifier; `tfidf_vectorizer.joblib` is its vectorizer; `metrics.json` contains evaluation results.

## Configuration

Example files are provided at `backend/.env.example` and `frontend/.env.example`.

Backend settings include:

| Variable | Purpose |
|---|---|
| `FLASK_ENV` | Selects development or production configuration |
| `PORT` | Backend port (defaults to `5000`) |
| `DATABASE_URL` | SQLAlchemy database connection (defaults to local SQLite) |
| `CORS_ORIGINS` | Comma-separated frontend origins allowed by CORS |
| `MAX_CONTENT_LENGTH` | Maximum upload request size in bytes (default: 16 MiB) |
| `UPLOAD_FOLDER` | Temporary upload directory |
| `SECRET_KEY` | Flask secret key; use a private, strong value outside local development |

The frontend accepts `VITE_API_BASE_URL` (or `VITE_API_URL`) to override its default API base URL, `http://localhost:5000/api/v1`.

## Tests and quality checks

Run the backend tests from the project root:

```powershell
.\venv\Scripts\pytest.exe -o pythonpath=. backend\tests
```

Build the frontend:

```powershell
cd frontend
npm run build
```

Lint the frontend:

```powershell
npm run lint
```

## Privacy and limitations

- Resume parsing, analysis, the database, and inference run locally in this application setup; no paid AI API is used.
- Uploaded resume text and extracted personal details are stored in the local SQLite database until the corresponding data is deleted.
- The frontend loads Google Fonts from Google Fonts, and curated learning links may point to external websites.
- Training and evaluation datasets are synthetic. Results on them do not establish real-world model performance.
- The analysis is intended as career guidance, not an automated employment or hiring decision.
- The Flask development server is for local development and is not a production deployment server.

## Additional documentation

- [System architecture](./docs/architecture.md)
- [API specification](./docs/api.md)
- [Machine-learning methodology](./docs/ml_methodology.md)
- [Synthetic dataset dictionary](./docs/dataset.md)
- [User guide](./docs/user_guide.md)

Some existing documents may describe screens or model claims that have since changed; the root README reflects the current frontend routes and code reviewed for this update.

## License

The previous README identified this project as MIT-licensed, but there is currently no `LICENSE` file in the repository. Add the license text file if you need to formally include and distribute those terms with the project.
