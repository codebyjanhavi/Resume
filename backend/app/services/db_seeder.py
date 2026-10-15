"""Seed SQLite with skill taxonomy, roles, requirements, and learning resources."""

import os
import json
import pandas as pd
from backend.app.extensions import db
from backend.app.models.models import JobRole, Skill, RoleSkillRequirement, LearningResource
from backend.app.services.matching_engine import CURATED_RESOURCES

def seed_database_if_empty(app):
    """
    Seeds job roles, skills taxonomy, requirements, and curated resources into SQLite database.
    """
    with app.app_context():
        # Check if already seeded
        if JobRole.query.first() is not None:
            return
            
        data_dir = app.config.get("DATA_DIR")
        tax_path = os.path.join(data_dir, "skills_taxonomy.csv")
        req_path = os.path.join(data_dir, "role_skill_requirements.csv")
        
        if not os.path.exists(tax_path) or not os.path.exists(req_path):
            print(f"[WARN] Data files missing at {data_dir}. Skipping database seed.")
            return
            
        print("[DB] Seeding Skills Taxonomy and Job Roles from synthetic assets...")
        
        # 1. Seed Skills
        df_tax = pd.read_csv(tax_path)
        skill_map = {}  # name -> Skill instance
        for _, row in df_tax.iterrows():
            aliases = [a.strip() for a in str(row.get("aliases", "")).split(";") if a.strip()]
            skill_obj = Skill(
                name=row["skill_name"],
                category=row["category"],
                default_weight=float(row.get("weight", 1.0)),
                aliases_json=json.dumps(aliases)
            )
            db.session.add(skill_obj)
            skill_map[row["skill_name"]] = skill_obj
            
        db.session.flush()
        
        # 2. Seed Job Roles and Requirements
        df_reqs = pd.read_csv(req_path)
        roles_dict = {}  # title -> JobRole instance
        
        for _, row in df_reqs.iterrows():
            role_title = row["role_title"]
            if role_title not in roles_dict:
                cat = "Engineering"
                if "Data" in role_title or "Analyst" in role_title or "AI" in role_title:
                    cat = "Data & AI"
                elif "Cloud" in role_title or "DevOps" in role_title:
                    cat = "Cloud & Infrastructure"
                elif "Security" in role_title:
                    cat = "Security"
                elif "Business" in role_title:
                    cat = "Business"
                    
                role_obj = JobRole(
                    title=role_title,
                    category=cat,
                    description=str(row.get("role_description", f"Professional role for {role_title}"))
                )
                db.session.add(role_obj)
                roles_dict[role_title] = role_obj
                
        db.session.flush()
        
        for _, row in df_reqs.iterrows():
            role_title = row["role_title"]
            skill_name = row["skill_name"]
            req_type = row["requirement_type"]
            weight = float(row.get("importance_weight", 1.0))
            
            role_obj = roles_dict.get(role_title)
            skill_obj = skill_map.get(skill_name)
            
            # If skill not yet in taxonomy, create it
            if not skill_obj:
                skill_obj = Skill(name=skill_name, category="General", default_weight=1.0, aliases_json="[]")
                db.session.add(skill_obj)
                db.session.flush()
                skill_map[skill_name] = skill_obj
                
            if role_obj and skill_obj:
                req_obj = RoleSkillRequirement(
                    role_id=role_obj.id,
                    skill_id=skill_obj.id,
                    requirement_type=req_type,
                    importance_weight=weight
                )
                db.session.add(req_obj)
                
        # 3. Seed Curated Learning Resources
        for s_name, res_list in CURATED_RESOURCES.items():
            for r in res_list:
                res_obj = LearningResource(
                    skill_name=s_name,
                    title=r["title"],
                    resource_type=r["type"],
                    provider=r["provider"],
                    url=r["url"],
                    is_free=True
                )
                db.session.add(res_obj)
                
        db.session.commit()
        print(f"[DB SUCCESS] Seeded {len(skill_map)} skills, {len(roles_dict)} roles, and resources.")
