"""Implement the REST API for resumes, skill analysis, roles, roadmaps, and reports."""

import os
import json
from io import BytesIO
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models.models import (
    Resume, ExtractedSkill, JobRole, Skill, RoleSkillRequirement,
    Analysis, AnalysisSkill, LearningRoadmap, RoadmapItem, LearningResource
)
from backend.app.services.document_parser import (
    extract_text_from_file, extract_contact_info, detect_sections
)
from backend.app.services.skill_extractor import skill_extractor
from backend.app.services.matching_engine import MatchingEngine
from backend.app.services.pdf_report_generator import generate_pdf_report
from backend.app.ml.predictor import predictor

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# 1. Health
@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "SkillSight AI Backend",
        "version": "1.0.0",
        "ml_model_loaded": predictor.model is not None,
    }), 200

# 2. Roles & Skills
@api_bp.route("/roles", methods=["GET"])
def get_roles():
    roles = JobRole.query.order_by(JobRole.title).all()
    return jsonify({"roles": [r.to_dict() for r in roles]}), 200

@api_bp.route("/skills", methods=["GET"])
def get_skills():
    skills = Skill.query.order_by(Skill.name).all()
    return jsonify({"skills": [s.to_dict() for s in skills]}), 200

# 3. Resumes Upload & Management
@api_bp.route("/resumes", methods=["POST"])
def upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
        
    orig_name = file.filename
    ext = Path(orig_name).suffix.lower().replace(".", "")
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "docx", "txt"})
    if ext not in allowed and ext != "txt":
        return jsonify({"error": f"Invalid file type .{ext}. Allowed: PDF, DOCX, TXT"}), 400
        
    safe_name = secure_filename(orig_name)
    upload_folder = current_app.config.get("UPLOAD_FOLDER")
    os.makedirs(upload_folder, exist_ok=True)
    temp_path = os.path.join(upload_folder, safe_name)
    file.save(temp_path)
    
    try:
        # Extract plain text
        raw_text = extract_text_from_file(temp_path, safe_name)
        file_size = os.path.getsize(temp_path)
        
        # Clean up temporary uploaded file if configured
        if current_app.config.get("CLEANUP_TEMP_FILES", True):
            try:
                os.remove(temp_path)
            except Exception:
                pass
                
        # Parse contact information & sections
        contact_info = extract_contact_info(raw_text)
        sections = detect_sections(raw_text)
        
        # Estimate experience years heuristic from text
        exp_years = 0.0
        exp_section = sections.get("Experience", "")
        if exp_section:
            import re
            year_matches = re.findall(r'\b(20\d\d|19\d\d)\b', exp_section)
            if len(year_matches) >= 2:
                years = [int(y) for y in year_matches]
                exp_years = min(20.0, max(0.0, float(max(years) - min(years))))
                
        # Create Resume DB record
        resume = Resume(
            filename=safe_name,
            original_filename=orig_name,
            file_type=ext,
            file_size_bytes=file_size,
            raw_text=raw_text,
            candidate_name=contact_info.get("candidate_name", "Candidate"),
            email=contact_info.get("email"),
            phone=contact_info.get("phone"),
            experience_years=exp_years,
            sections_json=json.dumps(sections)
        )
        db.session.add(resume)
        db.session.flush()
        
        # Extract skills using boundary-aware NLP engine
        extracted = skill_extractor.extract_from_sections(sections)
        if not extracted:
            extracted = skill_extractor.extract_skills(raw_text, section_name="Full Document")
            
        skill_objects = []
        for s_data in extracted:
            es = ExtractedSkill(
                resume_id=resume.id,
                skill_name=s_data["skill_name"],
                category=s_data["category"],
                confidence=s_data.get("confidence", 1.0),
                source_section=s_data.get("source_section", "Full Document"),
                is_confirmed=True
            )
            db.session.add(es)
            skill_objects.append(es)
            
        db.session.commit()
        
        return jsonify({
            "message": "Resume uploaded and parsed successfully",
            "resume": resume.to_dict(),
            "extracted_skills": [es.to_dict() for es in skill_objects]
        }), 201
        
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500

@api_bp.route("/resumes/<int:resume_id>", methods=["GET"])
def get_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    skills = ExtractedSkill.query.filter_by(resume_id=resume.id).all()
    return jsonify({
        "resume": resume.to_dict(),
        "skills": [s.to_dict() for s in skills]
    }), 200

@api_bp.route("/resumes/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"message": f"Resume {resume_id} deleted successfully"}), 200

@api_bp.route("/resumes/<int:resume_id>/skills", methods=["PUT"])
def update_resume_skills(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    data = request.get_json() or {}
    new_skills = data.get("skills", [])
    
    # Clear existing and replace with user-confirmed list
    ExtractedSkill.query.filter_by(resume_id=resume.id).delete()
    
    created = []
    for s in new_skills:
        name = s.get("skill_name") or s.get("name")
        if not name:
            continue
        cat = s.get("category", "General")
        es = ExtractedSkill(
            resume_id=resume.id,
            skill_name=name,
            category=cat,
            confidence=float(s.get("confidence", 1.0)),
            source_section=s.get("source_section", "User Confirmed"),
            is_confirmed=bool(s.get("is_confirmed", True))
        )
        db.session.add(es)
        created.append(es)
        
    db.session.commit()
    return jsonify({"message": "Skills updated successfully", "skills": [c.to_dict() for c in created]}), 200

# 4. Analysis Execution & Retrieval
@api_bp.route("/analysis", methods=["POST"])
def run_analysis():
    data = request.get_json() or {}
    resume_id = data.get("resume_id")
    target_role_id = data.get("target_role_id")
    custom_jd = data.get("custom_job_description")
    confirmed_skills = data.get("confirmed_skills")
    
    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400
        
    resume = Resume.query.get_or_404(resume_id)
    
    # Determine candidate skills to evaluate
    if confirmed_skills is not None:
        candidate_skills = confirmed_skills
    else:
        existing_skills = ExtractedSkill.query.filter_by(resume_id=resume.id, is_confirmed=True).all()
        candidate_skills = [s.skill_name for s in existing_skills]
        
    # Target role resolution
    target_role = None
    target_jd_text = ""
    mandatory_reqs = []
    preferred_reqs = []
    
    if target_role_id:
        target_role = JobRole.query.get(target_role_id)
        if target_role:
            target_jd_text = target_role.description
            for r in target_role.requirements:
                if r.requirement_type == "mandatory":
                    mandatory_reqs.append((r.skill.name, r.importance_weight))
                else:
                    preferred_reqs.append((r.skill.name, r.importance_weight))
                    
    elif custom_jd:
        target_jd_text = custom_jd
        # Extract skills from custom JD
        jd_skills = skill_extractor.extract_skills(custom_jd)
        for s in jd_skills[:8]:
            mandatory_reqs.append((s["skill_name"], 1.0))
        for s in jd_skills[8:]:
            preferred_reqs.append((s["skill_name"], 0.6))
    else:
        # Default to first role if not specified
        target_role = JobRole.query.first()
        if target_role:
            target_role_id = target_role.id
            target_jd_text = target_role.description
            for r in target_role.requirements:
                if r.requirement_type == "mandatory":
                    mandatory_reqs.append((r.skill.name, r.importance_weight))
                else:
                    preferred_reqs.append((r.skill.name, r.importance_weight))
                    
    # Model A: Machine Learning Job-Role Prediction
    prediction_result = predictor.predict(resume.raw_text, top_n=3)
    predicted_role = prediction_result["predicted_role"]
    confidence = prediction_result["confidence"]
    alternatives = prediction_result["alternatives"]
    
    # Model B: Resume-to-Job Text Similarity (Cosine Similarity)
    text_sim = MatchingEngine.calculate_text_similarity(resume.raw_text, target_jd_text)
    
    # Model C: Skill Compatibility Engine
    comp_result = MatchingEngine.calculate_skill_compatibility(
        candidate_skills, mandatory_reqs, preferred_reqs
    )
    
    # Heuristic Resume Suggestions
    sections = resume.get_sections()
    suggestions = MatchingEngine.generate_resume_suggestions(
        sections,
        resume.raw_text,
        matched_count=len(comp_result["matched_skills"]),
        missing_mandatory_count=len(comp_result["missing_mandatory_skills"])
    )
    
    # Create Analysis Record
    analysis = Analysis(
        resume_id=resume.id,
        target_role_id=target_role_id,
        custom_job_description=custom_jd,
        predicted_role=predicted_role,
        predicted_role_confidence=confidence,
        alternative_roles_json=json.dumps(alternatives),
        text_similarity_score=text_sim,
        overall_skill_coverage=comp_result["overall_skill_coverage"],
        mandatory_skill_coverage=comp_result["mandatory_skill_coverage"],
        suggestions_json=json.dumps(suggestions)
    )
    db.session.add(analysis)
    db.session.flush()
    
    # Add Analysis Skills breakdown
    all_categorized = (
        comp_result["matched_skills"] +
        comp_result["missing_mandatory_skills"] +
        comp_result["missing_preferred_skills"] +
        comp_result["additional_skills"]
    )
    for s_item in all_categorized:
        askill = AnalysisSkill(
            analysis_id=analysis.id,
            skill_name=s_item["skill_name"],
            status=s_item["status"],
            category=s_item.get("category", "General"),
            weight=s_item.get("weight", 1.0)
        )
        db.session.add(askill)
        
    # Model D: Personalized Learning Roadmap
    roadmap_items_data = MatchingEngine.generate_recommendations_and_roadmap(
        comp_result["missing_mandatory_skills"],
        comp_result["missing_preferred_skills"],
        target_role.title if target_role else "Target Role"
    )
    
    roadmap = LearningRoadmap(
        analysis_id=analysis.id,
        title=f"Roadmap: {target_role.title if target_role else 'Career Advancement'}",
        total_items=len(roadmap_items_data),
        completed_items=0
    )
    db.session.add(roadmap)
    db.session.flush()
    
    for r_item in roadmap_items_data:
        ritem_obj = RoadmapItem(
            roadmap_id=roadmap.id,
            skill_name=r_item["skill_name"],
            priority=r_item["priority"],
            stage=r_item["stage"],
            reason=r_item["reason"],
            suggested_project=r_item.get("suggested_project"),
            resources_json=json.dumps(r_item.get("resources", [])),
            status="not_started",
            estimated_hours=r_item.get("estimated_hours", 20)
        )
        db.session.add(ritem_obj)
        
    db.session.commit()
    
    return jsonify({
        "message": "Analysis completed successfully",
        "analysis": analysis.to_dict()
    }), 201

@api_bp.route("/analysis/<int:analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    return jsonify({"analysis": analysis.to_dict()}), 200

@api_bp.route("/analysis", methods=["GET"])
def list_analyses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    pagination = Analysis.query.order_by(Analysis.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "analyses": [a.to_dict() for a in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    }), 200

@api_bp.route("/analysis/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    db.session.delete(analysis)
    db.session.commit()
    return jsonify({"message": f"Analysis {analysis_id} deleted successfully"}), 200

# 5. Multi-Role Comparison
@api_bp.route("/roles/compare", methods=["POST"])
def compare_roles():
    data = request.get_json() or {}
    resume_id = data.get("resume_id")
    role_ids = data.get("role_ids", [])
    
    if not resume_id or not role_ids:
        return jsonify({"error": "resume_id and role_ids list are required"}), 400
        
    resume = Resume.query.get_or_404(resume_id)
    candidate_skills = [s.skill_name for s in resume.extracted_skills if s.is_confirmed]
    
    comparisons = []
    for r_id in role_ids:
        role = JobRole.query.get(r_id)
        if not role:
            continue
            
        mandatory_reqs = [(r.skill.name, r.importance_weight) for r in role.requirements if r.requirement_type == "mandatory"]
        preferred_reqs = [(r.skill.name, r.importance_weight) for r in role.requirements if r.requirement_type == "preferred"]
        
        comp = MatchingEngine.calculate_skill_compatibility(candidate_skills, mandatory_reqs, preferred_reqs)
        
        comparisons.append({
            "role": role.to_dict(),
            "mandatory_coverage": comp["mandatory_skill_coverage"],
            "overall_coverage": comp["overall_skill_coverage"],
            "matched_count": len(comp["matched_skills"]),
            "missing_mandatory_count": len(comp["missing_mandatory_skills"]),
            "missing_preferred_count": len(comp["missing_preferred_skills"])
        })
        
    return jsonify({"comparisons": comparisons}), 200

# 6. Roadmaps & Roadmap Items
@api_bp.route("/roadmaps/<int:analysis_id>", methods=["GET"])
def get_roadmap(analysis_id):
    roadmap = LearningRoadmap.query.filter_by(analysis_id=analysis_id).first_or_404()
    return jsonify({"roadmap": roadmap.to_dict()}), 200

@api_bp.route("/roadmaps/<int:roadmap_id>/items/<int:item_id>", methods=["PATCH"])
def update_roadmap_item(roadmap_id, item_id):
    item = RoadmapItem.query.filter_by(id=item_id, roadmap_id=roadmap_id).first_or_404()
    data = request.get_json() or {}
    new_status = data.get("status")
    
    if new_status not in ["not_started", "in_progress", "completed"]:
        return jsonify({"error": "Invalid status value. Allowed: not_started, in_progress, completed"}), 400
        
    item.status = new_status
    db.session.commit()
    
    return jsonify({"message": "Item updated", "item": item.to_dict()}), 200

# 7. Dashboard Metrics
@api_bp.route("/metrics/dashboard", methods=["GET"])
def get_dashboard_metrics():
    total_analyses = Analysis.query.count()
    if total_analyses == 0:
        return jsonify({
            "total_analyses": 0,
            "avg_compatibility_score": 0.0,
            "most_missing_skills": [],
            "most_matched_skills": [],
            "top_recommended_roles": [],
            "recent_analyses": [],
            "skill_gap_distribution": [
                {"range": "0-25%", "count": 0},
                {"range": "25-50%", "count": 0},
                {"range": "50-75%", "count": 0},
                {"range": "75-100%", "count": 0}
            ]
        }), 200
        
    avg_score = db.session.query(func.avg(Analysis.overall_skill_coverage)).scalar() or 0.0
    
    # Most missing mandatory skills
    missing_query = db.session.query(
        AnalysisSkill.skill_name, func.count(AnalysisSkill.id).label("cnt")
    ).filter(AnalysisSkill.status == "missing_mandatory").group_by(AnalysisSkill.skill_name).order_by(func.count(AnalysisSkill.id).desc()).limit(6).all()
    
    # Most matched skills
    matched_query = db.session.query(
        AnalysisSkill.skill_name, func.count(AnalysisSkill.id).label("cnt")
    ).filter(AnalysisSkill.status == "matched").group_by(AnalysisSkill.skill_name).order_by(func.count(AnalysisSkill.id).desc()).limit(6).all()
    
    # Top recommended roles
    roles_query = db.session.query(
        Analysis.predicted_role, func.count(Analysis.id).label("cnt")
    ).group_by(Analysis.predicted_role).order_by(func.count(Analysis.id).desc()).limit(5).all()
    
    # Recent analyses
    recent = Analysis.query.order_by(Analysis.created_at.desc()).limit(5).all()
    
    # Skill gap distribution
    c1 = Analysis.query.filter(Analysis.overall_skill_coverage < 25).count()
    c2 = Analysis.query.filter(Analysis.overall_skill_coverage >= 25, Analysis.overall_skill_coverage < 50).count()
    c3 = Analysis.query.filter(Analysis.overall_skill_coverage >= 50, Analysis.overall_skill_coverage < 75).count()
    c4 = Analysis.query.filter(Analysis.overall_skill_coverage >= 75).count()
    
    return jsonify({
        "total_analyses": total_analyses,
        "avg_compatibility_score": round(float(avg_score), 1),
        "most_missing_skills": [{"name": m[0], "count": m[1]} for m in missing_query],
        "most_matched_skills": [{"name": m[0], "count": m[1]} for m in matched_query],
        "top_recommended_roles": [{"role": r[0], "count": r[1]} for r in roles_query],
        "recent_analyses": [a.to_dict() for a in recent],
        "skill_gap_distribution": [
            {"range": "0-25%", "count": c1},
            {"range": "25-50%", "count": c2},
            {"range": "50-75%", "count": c3},
            {"range": "75-100%", "count": c4}
        ]
    }), 200

# 8. Model Metrics
@api_bp.route("/models/metrics", methods=["GET"])
def get_model_metrics():
    metrics = predictor.get_metrics()
    return jsonify({"metrics": metrics}), 200

# 9. Reports (PDF and JSON export)
@api_bp.route("/reports/<int:analysis_id>/pdf", methods=["GET"])
def download_pdf_report(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    pdf_buffer = generate_pdf_report(analysis.to_dict())
    
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"SkillSight_Analysis_{analysis.id}.pdf"
    )

@api_bp.route("/reports/<int:analysis_id>/json", methods=["GET"])
def get_report_json(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    return jsonify({"report": analysis.to_dict()}), 200
