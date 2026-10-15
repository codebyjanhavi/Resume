# SkillSight AI — User Guide

## Start the application

Start the backend and frontend in separate PowerShell terminals.

Backend, from the project root:

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap"
.\venv\Scripts\python.exe backend\run.py
```

Frontend, in a second terminal:

```powershell
cd "c:\Users\santo\OneDrive\Desktop\Resume_Skill_Gap\frontend"
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173/`. If it chooses another port because 5173 is busy, that frontend origin must also be permitted in the backend's `CORS_ORIGINS` configuration.

## Overview dashboard

The Overview page shows aggregate resume-analysis counts, average skill compatibility, commonly missing skills, skill-gap charts with colored coverage-tier legends, and recent analyses. Use the **View All** link to open Analysis History. Classifier architecture/accuracy and pipeline status cards are not displayed in the current dashboard.

## Analyze a resume

1. Open **Analyze Resume**.
2. Select or drop a `.pdf`, `.docx`, or `.txt` resume and upload it.
3. Review the extracted skills. Add skills that were missed and remove incorrect matches.
4. Select a predefined target job role or provide a custom job description.
5. Submit the analysis.
6. On the results page, review the predicted role and alternatives, compatibility and mandatory coverage, text similarity, skill matches/gaps, and heuristic resume suggestions.
7. Download the PDF report from the results page if desired.

Text extraction is local. Scanned/image-only PDFs are not OCR-processed and may not yield readable text.

## History and reports

- **Analysis History** lists saved analyses. Open a result or delete an analysis from the list.
- **Reports** lists available analyses and provides report download links.
- Reports can be retrieved as PDF or JSON through the API.

## Roles, roadmaps, and API-only features

The current frontend navigation is **Overview**, **Analyze Resume**, **Analysis History**, and **Reports**. There is no dedicated Job Role Explorer, Skill Intelligence, Learning Roadmap, or Settings page. Role selection is available during resume analysis. The backend still provides role comparison and roadmap endpoints; these can be accessed by API clients.

## Data handling

Parsed resume text and extracted contact information are stored in the local SQLite database. The uploaded file is temporarily placed in `backend/uploads/` for parsing and is configured for cleanup after processing. Deleting only the temporary upload does not erase the database record. Analysis History provides a control to delete an analysis; use the resume deletion API to delete a stored resume and its related data.

All bundled classifier training data is synthetic. Predictions and compatibility scores are intended for career exploration and self-assessment, not automated hiring decisions.
