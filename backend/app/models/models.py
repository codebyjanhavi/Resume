"""Define SQLAlchemy models for resumes, skills, analyses, roles, and learning resources."""

from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from backend.app.extensions import db

def utcnow():
    return datetime.now(timezone.utc)

class Resume(db.Model):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    file_size_bytes = Column(Integer, default=0)
    raw_text = Column(Text, nullable=False)
    
    candidate_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    education_summary = Column(Text, nullable=True)
    experience_years = Column(Float, default=0.0)
    sections_json = Column(Text, default="{}")  # JSON string of detected sections
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    extracted_skills = relationship("ExtractedSkill", back_populates="resume", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")

    def get_sections(self):
        try:
            return json.loads(self.sections_json) if self.sections_json else {}
        except Exception:
            return {}

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size_bytes": self.file_size_bytes,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "phone": self.phone,
            "education_summary": self.education_summary,
            "experience_years": self.experience_years,
            "sections": self.get_sections(),
            "skills_count": len(self.extracted_skills),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class ExtractedSkill(db.Model):
    __tablename__ = "extracted_skills"
    
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), default="General")
    confidence = Column(Float, default=1.0)
    source_section = Column(String(100), default="Skills")
    is_confirmed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    resume = relationship("Resume", back_populates="extracted_skills")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "skill_name": self.skill_name,
            "category": self.category,
            "confidence": self.confidence,
            "source_section": self.source_section,
            "is_confirmed": self.is_confirmed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class JobRole(db.Model):
    __tablename__ = "job_roles"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    requirements = relationship("RoleSkillRequirement", back_populates="job_role", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="target_role")

    def to_dict(self):
        mandatory = [r.skill.name for r in self.requirements if r.requirement_type == "mandatory" and r.skill]
        preferred = [r.skill.name for r in self.requirements if r.requirement_type == "preferred" and r.skill]
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "mandatory_skills": mandatory,
            "preferred_skills": preferred,
            "total_skills_required": len(mandatory) + len(preferred)
        }

class Skill(db.Model):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    default_weight = Column(Float, default=1.0)
    aliases_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=utcnow)
    
    requirements = relationship("RoleSkillRequirement", back_populates="skill")

    def get_aliases(self):
        try:
            return json.loads(self.aliases_json) if self.aliases_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "default_weight": self.default_weight,
            "aliases": self.get_aliases()
        }

class RoleSkillRequirement(db.Model):
    __tablename__ = "role_skill_requirements"
    
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    requirement_type = Column(String(20), nullable=False)  # mandatory, preferred
    importance_weight = Column(Float, default=1.0)
    
    job_role = relationship("JobRole", back_populates="requirements")
    skill = relationship("Skill", back_populates="requirements")

    def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "role_title": self.job_role.title if self.job_role else None,
            "skill_id": self.skill_id,
            "skill_name": self.skill.name if self.skill else None,
            "requirement_type": self.requirement_type,
            "importance_weight": self.importance_weight
        }

class Analysis(db.Model):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="SET NULL"), nullable=True, index=True)
    custom_job_description = Column(Text, nullable=True)
    
    # ML Outputs
    predicted_role = Column(String(150), nullable=False)
    predicted_role_confidence = Column(Float, default=0.0)
    alternative_roles_json = Column(Text, default="[]")
    
    # Scores
    text_similarity_score = Column(Float, default=0.0)       # 0 - 100%
    overall_skill_coverage = Column(Float, default=0.0)      # 0 - 100%
    mandatory_skill_coverage = Column(Float, default=0.0)    # 0 - 100%
    
    # Heuristic Resume Suggestions
    suggestions_json = Column(Text, default="[]")
    
    created_at = Column(DateTime, default=utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    target_role = relationship("JobRole", back_populates="analyses")
    skills_breakdown = relationship("AnalysisSkill", back_populates="analysis", cascade="all, delete-orphan")
    roadmap = relationship("LearningRoadmap", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

    def get_alternatives(self):
        try:
            return json.loads(self.alternative_roles_json) if self.alternative_roles_json else []
        except Exception:
            return []

    def get_suggestions(self):
        try:
            return json.loads(self.suggestions_json) if self.suggestions_json else []
        except Exception:
            return []

    def to_dict(self):
        matched = [s.to_dict() for s in self.skills_breakdown if s.status == "matched"]
        missing_mand = [s.to_dict() for s in self.skills_breakdown if s.status == "missing_mandatory"]
        missing_pref = [s.to_dict() for s in self.skills_breakdown if s.status == "missing_preferred"]
        additional = [s.to_dict() for s in self.skills_breakdown if s.status == "additional"]
        
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "resume_filename": self.resume.original_filename if self.resume else None,
            "candidate_name": self.resume.candidate_name if self.resume else None,
            "target_role_id": self.target_role_id,
            "target_role_title": self.target_role.title if self.target_role else "Custom Job Description",
            "has_custom_jd": bool(self.custom_job_description),
            "predicted_role": self.predicted_role,
            "predicted_role_confidence": round(self.predicted_role_confidence, 2),
            "alternative_roles": self.get_alternatives(),
            "text_similarity_score": round(self.text_similarity_score, 1),
            "overall_skill_coverage": round(self.overall_skill_coverage, 1),
            "mandatory_skill_coverage": round(self.mandatory_skill_coverage, 1),
            "matched_skills": matched,
            "missing_mandatory_skills": missing_mand,
            "missing_preferred_skills": missing_pref,
            "additional_skills": additional,
            "suggestions": self.get_suggestions(),
            "roadmap_id": self.roadmap.id if self.roadmap else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class AnalysisSkill(db.Model):
    __tablename__ = "analysis_skills"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False)  # matched, missing_mandatory, missing_preferred, additional
    category = Column(String(100), default="General")
    weight = Column(Float, default=1.0)
    
    analysis = relationship("Analysis", back_populates="skills_breakdown")

    def to_dict(self):
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "status": self.status,
            "category": self.category,
            "weight": self.weight
        }

class LearningRoadmap(db.Model):
    __tablename__ = "learning_roadmaps"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    analysis = relationship("Analysis", back_populates="roadmap")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapItem.id")

    def to_dict(self):
        items_list = [item.to_dict() for item in self.items]
        completed = sum(1 for it in items_list if it["status"] == "completed")
        progress = round((completed / len(items_list) * 100), 1) if items_list else 0
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "title": self.title,
            "total_items": len(items_list),
            "completed_items": completed,
            "progress_percentage": progress,
            "items": items_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class RoadmapItem(db.Model):
    __tablename__ = "roadmap_items"
    
    id = Column(Integer, primary_key=True)
    roadmap_id = Column(Integer, ForeignKey("learning_roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    priority = Column(String(20), default="medium")  # high, medium, low
    stage = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    reason = Column(Text, nullable=False)
    suggested_project = Column(Text, nullable=True)
    resources_json = Column(Text, default="[]")
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    estimated_hours = Column(Integer, default=20)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    roadmap = relationship("LearningRoadmap", back_populates="items")

    def get_resources(self):
        try:
            return json.loads(self.resources_json) if self.resources_json else []
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "roadmap_id": self.roadmap_id,
            "skill_name": self.skill_name,
            "priority": self.priority,
            "stage": self.stage,
            "reason": self.reason,
            "suggested_project": self.suggested_project,
            "resources": self.get_resources(),
            "status": self.status,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class LearningResource(db.Model):
    __tablename__ = "learning_resources"
    
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    resource_type = Column(String(50), default="Tutorial")  # Course, Documentation, Tutorial, Guide
    provider = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    is_free = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "title": self.title,
            "resource_type": self.resource_type,
            "provider": self.provider,
            "url": self.url,
            "is_free": self.is_free,
        }
