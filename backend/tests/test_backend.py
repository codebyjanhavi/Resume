"""Test backend APIs, resume processing, matching, prediction, and PDF reports."""

import os
import json
import pytest
from io import BytesIO

from backend.app import create_app
from backend.app.extensions import db
from backend.app.services.skill_extractor import skill_extractor
from backend.app.services.matching_engine import MatchingEngine
from backend.app.services.document_parser import extract_contact_info, detect_sections
from backend.app.ml.predictor import predictor
from backend.app.services.pdf_report_generator import generate_pdf_report

@pytest.fixture
def app():
    os.environ["FLASK_ENV"] = "development"
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["ml_model_loaded"] is True

def test_roles_endpoint(client):
    res = client.get("/api/v1/roles")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["roles"]) >= 15
    titles = [r["title"] for r in data["roles"]]
    assert "Data Scientist" in titles
    assert "Machine Learning Engineer" in titles
    assert "DevOps Engineer" in titles

def test_skills_endpoint(client):
    res = client.get("/api/v1/skills")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["skills"]) >= 90

def test_skill_extractor_normalization_and_aliases():
    sample_text = """
    Proficient in Python, py, JS, react.js, k8s, tf, and PostgreSQL.
    Experience with Machine Learning and natural language processing.
    """
    extracted = skill_extractor.extract_skills(sample_text)
    skill_names = {s["skill_name"] for s in extracted}
    
    assert "Python" in skill_names
    assert "JavaScript" in skill_names
    assert "React" in skill_names
    assert "Kubernetes" in skill_names
    assert "TensorFlow" in skill_names
    assert "PostgreSQL" in skill_names
    assert "Machine Learning" in skill_names
    assert "NLP" in skill_names

def test_matching_engine_deterministic_scores():
    candidate_skills = ["Python", "Machine Learning", "Statistics", "Pandas"]
    mandatory_reqs = [
        ("Python", 1.0),
        ("Machine Learning", 1.0),
        ("Statistics", 1.0),
        ("SQL", 1.0),
    ]
    preferred_reqs = [
        ("Pandas", 0.6),
        ("Docker", 0.6),
    ]
    
    result = MatchingEngine.calculate_skill_compatibility(
        candidate_skills, mandatory_reqs, preferred_reqs
    )
    
    # 3 out of 4 mandatory matched = 75%
    assert result["mandatory_skill_coverage"] == 75.0
    # Overall coverage is deterministic and between 0 and 100
    assert 0.0 < result["overall_skill_coverage"] < 100.0
    
    matched_names = {s["skill_name"] for s in result["matched_skills"]}
    assert "Python" in matched_names
    assert "Machine Learning" in matched_names
    
    missing_mand = {s["skill_name"] for s in result["missing_mandatory_skills"]}
    assert "SQL" in missing_mand

def test_document_parser_contact_and_sections():
    resume_sample = """
    ALEX TAYLOR
    Email: alex.taylor@example.org | Phone: +1-555-0199
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 6 years experience building scalable web backends.
    
    TECHNICAL SKILLS
    Python, FastAPI, Docker, PostgreSQL, Redis, Git
    
    WORK EXPERIENCE
    Senior Engineer | Acme Corp | 2020 - 2024
    - Built microservices handling 5,000 RPS, reducing latency by 40%.
    
    EDUCATION
    BS in Computer Science | State University
    """
    contact = extract_contact_info(resume_sample)
    assert contact["email"] == "alex.taylor@example.org"
    assert contact["phone"] == "+1-555-0199"
    assert "ALEX" in contact["candidate_name"].upper()
    
    sections = detect_sections(resume_sample)
    assert "Summary" in sections or "Skills" in sections
    assert "Experience" in sections

def test_ml_model_prediction():
    text = "Machine Learning Engineer with deep expertise in PyTorch, TensorFlow, Deep Learning, and Computer Vision."
    pred = predictor.predict(text)
    assert pred["predicted_role"] in [
        "Machine Learning Engineer", "AI Engineer", "Data Scientist"
    ]
    assert pred["confidence"] > 0.0

def test_pdf_report_generation():
    mock_analysis = {
        "candidate_name": "Test Candidate",
        "target_role_title": "Data Scientist",
        "predicted_role": "Data Scientist",
        "predicted_role_confidence": 0.95,
        "resume_filename": "resume.pdf",
        "mandatory_skill_coverage": 85.0,
        "overall_skill_coverage": 88.5,
        "text_similarity_score": 72.0,
        "matched_skills": [{"skill_name": "Python"}, {"skill_name": "SQL"}],
        "missing_mandatory_skills": [{"skill_name": "Machine Learning"}],
        "missing_preferred_skills": [{"skill_name": "Deep Learning"}],
        "suggestions": [
            {"category": "Structure", "type": "strength", "message": "Good format", "details": "Structured well"}
        ]
    }
    pdf_buffer = generate_pdf_report(mock_analysis)
    assert pdf_buffer is not None
    assert pdf_buffer.getbuffer().nbytes > 1000
