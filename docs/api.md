# SkillSight AI — REST API

All endpoints are prefixed with `/api/v1`. The local development backend defaults to `http://127.0.0.1:5000`.

## System and catalogs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns service version, status, and whether the classifier loaded. |
| `GET` | `/roles` | Lists seeded roles and their requirements. |
| `GET` | `/skills` | Lists skills stored in the database. |

## Resumes

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/resumes` | Upload and parse a resume. Submit multipart form data with a `file` field; PDF, DOCX, and TXT are accepted. Returns resume data and extracted skills. |
| `GET` | `/resumes/{resume_id}` | Returns a resume and its extracted skills. |
| `DELETE` | `/resumes/{resume_id}` | Deletes a resume; related records follow database cascade rules. |
| `PUT` | `/resumes/{resume_id}/skills` | Replaces extracted skills with the submitted list. JSON body: `{"skills":[{"skill_name":"Python","category":"Programming Languages"}]}`. |

## Analysis and role comparison

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analysis` | Runs and stores resume analysis. |
| `GET` | `/analysis/{analysis_id}` | Returns one saved analysis. |
| `GET` | `/analysis?page=1&per_page=10` | Returns paginated analysis history, including total/page metadata. |
| `DELETE` | `/analysis/{analysis_id}` | Deletes a saved analysis. |
| `POST` | `/roles/compare` | Compares one resume with multiple role IDs. |

Analysis request example:

```json
{
  "resume_id": 1,
  "target_role_id": 3,
  "confirmed_skills": ["Python", "SQL"]
}
```

`resume_id` is required. The request may instead include a `custom_job_description`; if `confirmed_skills` is omitted, the backend uses the resume's confirmed extracted skills. The analysis response includes predicted role/confidence, text similarity, skill coverage, skill categories, and resume suggestions.

Role comparison request example:

```json
{
  "resume_id": 1,
  "role_ids": [1, 2, 3]
}
```

## Roadmaps

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/roadmaps/{analysis_id}` | Returns the roadmap created for an analysis. |
| `PATCH` | `/roadmaps/{roadmap_id}/items/{item_id}` | Changes a roadmap item's status. |

Valid status values are `not_started`, `in_progress`, and `completed`. Roadmap API functionality exists, but the current frontend does not have a dedicated roadmap page.

## Metrics and reports

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/metrics/dashboard` | Returns database-derived totals, average compatibility, skill frequency summaries, recent analyses, and compatibility-tier counts. |
| `GET` | `/models/metrics` | Returns training/evaluation metrics loaded from `backend/artifacts/metrics.json`. |
| `GET` | `/reports/{analysis_id}/pdf` | Downloads the generated PDF analysis report. |
| `GET` | `/reports/{analysis_id}/json` | Returns the analysis report as JSON. |

## Errors and implementation notes

- Missing database records use Flask-SQLAlchemy's `get_or_404`/`first_or_404` behavior.
- Resume upload and analysis validation errors return JSON error messages with an appropriate HTTP status.
- CORS origins are configured with `CORS_ORIGINS`; update this setting if the Vite frontend uses a port other than the default.
- This API is used by the local frontend and is not, by itself, a user-facing website at the backend root URL.
