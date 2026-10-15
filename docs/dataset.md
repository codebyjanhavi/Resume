# SkillSight AI — Synthetic Dataset Guide

## Purpose and privacy

The benchmark and training data under `backend/data/synthetic/` is procedurally generated fictional data. It is used for role-classifier training/evaluation and to seed the role and skill reference tables. It is not a collection of user-uploaded resumes. The generator uses a fixed random seed (`42`) for reproducibility.

The generator script is optional at runtime. The generated CSVs and model artifacts are included, so ordinary application startup does not require regenerating the data.

## Included files

### `synthetic_resumes.csv`

- **Rows:** 5,250; 350 profiles for each of 15 roles.
- **Use:** Source data for training and evaluating the job-role classifier.
- **Columns:** `candidate_id`, `full_name`, `email`, `phone`, `target_role`, `years_experience`, `degree`, `field_of_study`, `university`, `skills_list`, `certifications`, `projects_count`, `resume_text`, `is_synthetic`.
- `target_role` is the label; `resume_text` is the classifier's text input.

### `synthetic_job_descriptions.csv`

- **Rows:** 1,200; 80 job descriptions for each role.
- **Columns:** `job_id`, `role_title`, `company`, `experience_level`, `mandatory_skills`, `preferred_skills`, `description_text`, `is_synthetic`.
- This file provides synthetic benchmark examples. The current runtime analysis compares against a seeded role description or a user-provided job description; this CSV is not required by the API at startup.

### `skills_taxonomy.csv`

- **Rows:** 95 canonical skills in the included CSV.
- **Columns:** `skill_name`, `category`, `aliases`, `weight`.
- `aliases` contains semicolon-delimited alternate spellings or abbreviations.
- `backend/app/services/db_seeder.py` reads this file to populate the skills reference table when initializing an empty database.
- A related skill taxonomy is also defined in code in `backend/app/services/skill_extractor.py` for resume parsing.

### `role_skill_requirements.csv`

- **Rows:** 183 role-skill requirements in the included CSV.
- **Columns:** `role_title`, `skill_name`, `requirement_type`, `importance_weight`, `role_description`.
- Used by the database seeder to create predefined roles and their mandatory/preferred skill requirements.

### `synthetic_dataset_metadata.json`

Provides a dataset manifest with the seed, role list, record totals, synthetic-data notice, and filenames. Treat the CSV files as the source for their actual current row and column counts.

## Supported roles

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

## Regeneration and training

Regenerate the benchmark CSVs only if needed or intentionally desired:

```powershell
.\venv\Scripts\python.exe backend\scripts\generate_synthetic_data.py
```

Train a new classifier using the resume CSV:

```powershell
.\venv\Scripts\python.exe backend\scripts\train_models.py
```

Training overwrites the classifier, vectorizer, and metrics in `backend/artifacts/`. It is not required to run the application when the provided artifacts are available.
