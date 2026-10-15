"""Calculate resume-to-role skill matches and prepare learning recommendations."""

import re
from typing import List, Dict, Any, Set, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Curated catalog of high-quality learning resources
CURATED_RESOURCES = {
    "Python": [
        {"title": "Python Official Tutorial & Docs", "url": "https://docs.python.org/3/tutorial/", "type": "Documentation", "provider": "Python.org"},
        {"title": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com/", "type": "Book", "provider": "Al Sweigart"},
    ],
    "Machine Learning": [
        {"title": "Scikit-Learn Machine Learning in Python", "url": "https://scikit-learn.org/stable/tutorial/index.html", "type": "Documentation", "provider": "scikit-learn.org"},
        {"title": "Machine Learning Specialization", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "type": "Course", "provider": "DeepLearning.AI"},
    ],
    "Deep Learning": [
        {"title": "Deep Learning Specialization", "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/", "type": "Course", "provider": "DeepLearning.AI"},
        {"title": "PyTorch Deep Learning with Examples", "url": "https://pytorch.org/tutorials/beginner/pytorch_with_examples.html", "type": "Tutorial", "provider": "PyTorch"},
    ],
    "SQL": [
        {"title": "PostgreSQL Tutorial & Exercises", "url": "https://www.postgresqltutorial.com/", "type": "Tutorial", "provider": "PostgreSQL Tutorial"},
        {"title": "SQLZoo Interactive SQL Practice", "url": "https://sqlzoo.net/", "type": "Interactive", "provider": "SQLZoo"},
    ],
    "Docker": [
        {"title": "Docker Getting Started Guide", "url": "https://docs.docker.com/get-started/", "type": "Documentation", "provider": "Docker Docs"},
        {"title": "Docker for Beginners", "url": "https://docker-curriculum.com/", "type": "Tutorial", "provider": "Docker Curriculum"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Official Basics Tutorial", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "Documentation", "provider": "Kubernetes.io"},
    ],
    "React": [
        {"title": "React Official Documentation & Interactive Quickstart", "url": "https://react.dev/", "type": "Documentation", "provider": "React Core Team"},
    ],
    "TypeScript": [
        {"title": "TypeScript Handbook for Developers", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "type": "Documentation", "provider": "Microsoft"},
    ],
    "AWS": [
        {"title": "AWS Skill Builder Free Learning Plans", "url": "https://explore.skillbuilder.aws/", "type": "Course", "provider": "Amazon Web Services"},
    ],
    "Power BI": [
        {"title": "Microsoft Power BI Guided Learning", "url": "https://learn.microsoft.com/en-us/power-bi/guided-learning/", "type": "Course", "provider": "Microsoft Learn"},
    ],
    "Linux": [
        {"title": "Linux Journey: Interactive Command Line Lessons", "url": "https://linuxjourney.com/", "type": "Tutorial", "provider": "Linux Journey"},
    ],
    "Git": [
        {"title": "Pro Git Book & Official Reference", "url": "https://git-scm.com/book/en/v2", "type": "Book", "provider": "Git SCM"},
    ],
    "OWASP": [
        {"title": "OWASP Top Ten Web Application Security Risks", "url": "https://owasp.org/www-project-top-ten/", "type": "Documentation", "provider": "OWASP Foundation"},
    ],
    "FastAPI": [
        {"title": "FastAPI Tutorial - User Guide", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "Documentation", "provider": "Tiangolo"},
    ],
    "Pandas": [
        {"title": "Pandas 10 Minutes to Pandas", "url": "https://pandas.pydata.org/docs/user_guide/10min.html", "type": "Tutorial", "provider": "Pandas Team"},
    ]
}

# Project ideas by skill
PROJECT_SUGGESTIONS_BY_SKILL = {
    "Docker": "Containerize a multi-tier web application with separate database, API, and frontend services using Docker Compose.",
    "Kubernetes": "Deploy a containerized application to Minikube or cloud cluster with Deployments, Services, and Horizontal Pod Autoscalers.",
    "FastAPI": "Develop a high-performance RESTful API with Pydantic validation, OAuth2 JWT authentication, and automated OpenAPI documentation.",
    "Machine Learning": "Build a supervised classification or regression pipeline using Scikit-learn with feature engineering and cross-validation.",
    "Deep Learning": "Train a convolutional neural network with PyTorch for image classification or fine-tune a pre-trained ResNet model.",
    "SQL": "Design a normalized database schema with complex indexing, analytical window queries, and query execution plan optimization.",
    "React": "Build a responsive dashboard application with state management, custom hooks, and dynamic data visualizations.",
    "TypeScript": "Refactor a JavaScript project to TypeScript with strict mode, custom utility types, and complete type safety.",
    "AWS": "Deploy a serverless architecture using AWS Lambda, API Gateway, S3, and DynamoDB managed via Infrastructure as Code.",
    "Power BI": "Construct an executive sales analytics dashboard with DAX calculations, interactive slicers, and drill-down KPI visuals.",
    "OWASP": "Perform a simulated security audit on a sample web app, identifying vulnerabilities and implementing defense-in-depth mitigations.",
    "CI/CD": "Create a GitHub Actions automated workflow running linting, unit test suites, and container build/publish triggers.",
    "Linux": "Write automated shell maintenance scripts for system resource monitoring, log rotation, and cron scheduling.",
    "NLP": "Implement an end-to-end text classification or named-entity extraction pipeline using tokenization and TF-IDF / transformer embeddings.",
}

class MatchingEngine:
    @staticmethod
    def calculate_text_similarity(resume_text: str, job_text: str) -> float:
        """
        Calculate TF-IDF Cosine Similarity between resume text and job description.
        Returns percentage between 0.0 and 100.0%.
        """
        if not resume_text.strip() or not job_text.strip():
            return 0.0
            
        try:
            tfidf = TfidfVectorizer(stop_words="english", max_features=3000, sublinear_tf=True)
            tfidf_matrix = tfidf.fit_transform([resume_text, job_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Convert to percentage
            return float(np.clip(sim * 100.0, 0.0, 100.0))
        except Exception:
            return 0.0

    @staticmethod
    def calculate_skill_compatibility(
        candidate_skills: List[str],
        mandatory_requirements: List[Tuple[str, float]],  # list of (skill_name, weight)
        preferred_requirements: List[Tuple[str, float]],  # list of (skill_name, weight)
        taxonomy_dict: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Compare confirmed candidate skills against role requirements.
        Returns deterministic coverage percentages and categorized skill breakdowns.
        """
        cand_set = {s.strip().lower(): s.strip() for s in candidate_skills}
        
        matched_skills = []
        missing_mandatory_skills = []
        missing_preferred_skills = []
        
        total_mandatory_weight = sum(w for _, w in mandatory_requirements) or 1.0
        matched_mandatory_weight = 0.0
        
        # Check mandatory requirements
        for skill_name, weight in mandatory_requirements:
            canonical_lower = skill_name.strip().lower()
            cat = taxonomy_dict.get(skill_name, {}).get("category", "General") if taxonomy_dict else "General"
            
            if canonical_lower in cand_set:
                matched_mandatory_weight += weight
                matched_skills.append({
                    "skill_name": skill_name,
                    "status": "matched",
                    "category": cat,
                    "weight": weight,
                    "is_mandatory": True
                })
            else:
                missing_mandatory_skills.append({
                    "skill_name": skill_name,
                    "status": "missing_mandatory",
                    "category": cat,
                    "weight": weight,
                    "is_mandatory": True
                })
                
        # Check preferred requirements (weighted at 0.6)
        total_preferred_weight = sum(w for _, w in preferred_requirements) or 1.0
        matched_preferred_weight = 0.0
        
        for skill_name, weight in preferred_requirements:
            canonical_lower = skill_name.strip().lower()
            cat = taxonomy_dict.get(skill_name, {}).get("category", "General") if taxonomy_dict else "General"
            
            if canonical_lower in cand_set:
                matched_preferred_weight += weight
                matched_skills.append({
                    "skill_name": skill_name,
                    "status": "matched",
                    "category": cat,
                    "weight": weight,
                    "is_mandatory": False
                })
            else:
                missing_preferred_skills.append({
                    "skill_name": skill_name,
                    "status": "missing_preferred",
                    "category": cat,
                    "weight": weight,
                    "is_mandatory": False
                })
                
        # Additional candidate skills that are not required by this role
        required_names_lower = {s.lower() for s, _ in mandatory_requirements} | {s.lower() for s, _ in preferred_requirements}
        additional_skills = []
        for cand_lower, orig_name in cand_set.items():
            if cand_lower not in required_names_lower:
                cat = taxonomy_dict.get(orig_name, {}).get("category", "General") if taxonomy_dict else "General"
                additional_skills.append({
                    "skill_name": orig_name,
                    "status": "additional",
                    "category": cat,
                    "weight": 0.5,
                    "is_mandatory": False
                })
                
        # Calculations
        mandatory_coverage = (matched_mandatory_weight / total_mandatory_weight) * 100.0
        
        combined_total_weight = total_mandatory_weight + (0.6 * total_preferred_weight)
        combined_matched_weight = matched_mandatory_weight + (0.6 * matched_preferred_weight)
        overall_coverage = (combined_matched_weight / combined_total_weight) * 100.0 if combined_total_weight > 0 else 0.0
        
        return {
            "overall_skill_coverage": round(float(np.clip(overall_coverage, 0.0, 100.0)), 1),
            "mandatory_skill_coverage": round(float(np.clip(mandatory_coverage, 0.0, 100.0)), 1),
            "matched_skills": matched_skills,
            "missing_mandatory_skills": missing_mandatory_skills,
            "missing_preferred_skills": missing_preferred_skills,
            "additional_skills": additional_skills,
        }

    @staticmethod
    def generate_recommendations_and_roadmap(
        missing_mandatory: List[Dict[str, Any]],
        missing_preferred: List[Dict[str, Any]],
        target_role_title: str
    ) -> List[Dict[str, Any]]:
        """
        Model D: Generate ranked skill recommendations, milestones, and curated roadmap items.
        """
        roadmap_items = []
        
        # Mandatory gaps get High Priority
        for s in missing_mandatory:
            s_name = s["skill_name"]
            resources = CURATED_RESOURCES.get(s_name, [
                {"title": f"Complete Guide to {s_name}", "url": f"https://www.google.com/search?q={s_name}+documentation", "type": "Documentation", "provider": "Official"}
            ])
            project = PROJECT_SUGGESTIONS_BY_SKILL.get(
                s_name,
                f"Develop a portfolio application demonstrating core competency in {s_name} aligned with {target_role_title} requirements."
            )
            roadmap_items.append({
                "skill_name": s_name,
                "priority": "high",
                "stage": "beginner",
                "reason": f"Essential core competency required for the {target_role_title} role.",
                "suggested_project": project,
                "resources": resources,
                "status": "not_started",
                "estimated_hours": 30
            })
            
        # Preferred gaps get Medium/Low Priority
        for s in missing_preferred:
            s_name = s["skill_name"]
            resources = CURATED_RESOURCES.get(s_name, [
                {"title": f"{s_name} Essentials & Tutorials", "url": f"https://www.google.com/search?q={s_name}+tutorial", "type": "Tutorial", "provider": "Community"}
            ])
            project = PROJECT_SUGGESTIONS_BY_SKILL.get(
                s_name,
                f"Build a showcase feature or microservice implementing {s_name} best practices."
            )
            roadmap_items.append({
                "skill_name": s_name,
                "priority": "medium",
                "stage": "intermediate",
                "reason": f"High-value differentiator that elevates your competitiveness for {target_role_title}.",
                "suggested_project": project,
                "resources": resources,
                "status": "not_started",
                "estimated_hours": 20
            })
            
        return roadmap_items

    @staticmethod
    def generate_resume_suggestions(
        sections: Dict[str, str],
        resume_text: str,
        matched_count: int,
        missing_mandatory_count: int
    ) -> List[Dict[str, Any]]:
        """
        Evidence-based heuristic checks for resume improvement (Section 12).
        """
        suggestions = []
        
        # 1. Section presence checks
        expected_sections = ["Summary", "Skills", "Experience", "Projects", "Education"]
        for sec in expected_sections:
            if sec not in sections or not sections[sec].strip():
                suggestions.append({
                    "category": "Structure & Sections",
                    "type": "warning",
                    "message": f"Missing dedicated '{sec}' section.",
                    "details": f"Recruiters and automated ATS parsers expect an explicit '{sec}' section header."
                })
                
        # 2. Measurable impact / Metrics check
        # Search for metrics, percentages, currency, or quantifiable results in Experience or Projects
        exp_text = sections.get("Experience", "") + " " + sections.get("Projects", "")
        metric_matches = re.findall(r'(\d+%\s*|\$\d+[\d,]*|\b\d+\s*(?:users|clients|rps|ms|hours|x|times)\b)', exp_text, re.IGNORECASE)
        if len(metric_matches) < 2:
            suggestions.append({
                "category": "Impact & Measurable Outcomes",
                "type": "improvement",
                "message": "Quantify your achievements with concrete metrics.",
                "details": "Include specific percentages, latency improvements, user counts, or revenue metrics (e.g. 'reduced latency by 45%', 'processed 2M records daily')."
            })
        else:
            suggestions.append({
                "category": "Impact & Measurable Outcomes",
                "type": "strength",
                "message": f"Great quantifiable metrics detected ({len(metric_matches)} impact statements).",
                "details": "Your experience highlights tangible, results-oriented achievements."
            })
            
        # 3. Action verbs check
        action_verbs = ["engineered", "architected", "developed", "spearheaded", "optimized", "implemented", "deployed", "designed", "streamlined", "automated"]
        found_verbs = [v for v in action_verbs if re.search(rf'\b{v}\b', resume_text, re.IGNORECASE)]
        if len(found_verbs) < 3:
            suggestions.append({
                "category": "Action-Oriented Phrasing",
                "type": "improvement",
                "message": "Start experience bullets with strong action verbs.",
                "details": f"Use impactful active verbs such as {', '.join(action_verbs[:5])} to demonstrate ownership."
            })
            
        # 4. Target role skill alignment
        if missing_mandatory_count > 0:
            suggestions.append({
                "category": "Target Role Alignment",
                "type": "warning",
                "message": f"{missing_mandatory_count} mandatory skills are currently missing from your profile.",
                "details": "Highlight relevant coursework, open-source projects, or self-directed learning for missing core skills in your Technical Skills or Projects sections."
            })
            
        return suggestions
