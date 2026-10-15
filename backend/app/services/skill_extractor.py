"""Normalize skill aliases and extract categorized skills from resume text."""

import re
from typing import List, Dict, Any, Set, Tuple

# Comprehensive curated taxonomy with aliases and categories
DEFAULT_SKILL_TAXONOMY = {
    # Programming Languages
    "Python": {"category": "Programming Languages", "weight": 1.0, "aliases": ["python", "python3", "py"]},
    "Java": {"category": "Programming Languages", "weight": 1.0, "aliases": ["java", "core java", "java 17", "java 11", "java 8"]},
    "JavaScript": {"category": "Programming Languages", "weight": 1.0, "aliases": ["javascript", "js", "es6", "vanilla js"]},
    "TypeScript": {"category": "Programming Languages", "weight": 1.0, "aliases": ["typescript", "ts"]},
    "C": {"category": "Programming Languages", "weight": 0.8, "aliases": ["c lang", "c language"]},  # Handled carefully to avoid single 'c' false positives
    "C++": {"category": "Programming Languages", "weight": 0.9, "aliases": ["c++", "cpp", "cplusplus"]},
    "C#": {"category": "Programming Languages", "weight": 0.9, "aliases": ["c#", "csharp", "c sharp", ".net c#"]},
    "Kotlin": {"category": "Programming Languages", "weight": 0.8, "aliases": ["kotlin"]},
    "Go": {"category": "Programming Languages", "weight": 0.9, "aliases": ["golang", "go lang", "go programming"]},
    "PHP": {"category": "Programming Languages", "weight": 0.7, "aliases": ["php", "php7", "php8"]},
    "SQL": {"category": "Programming Languages", "weight": 1.0, "aliases": ["sql", "structured query language", "ansi sql", "tsql", "plsql", "pl/sql"]},
    "R": {"category": "Programming Languages", "weight": 0.8, "aliases": ["r lang", "rstats", "r language"]},
    "Rust": {"category": "Programming Languages", "weight": 0.8, "aliases": ["rust", "rustlang"]},
    "Scala": {"category": "Programming Languages", "weight": 0.8, "aliases": ["scala", "scala lang"]},
    "Shell Scripting": {"category": "Programming Languages", "weight": 0.8, "aliases": ["shell scripting", "bash", "sh", "zsh", "shell script"]},

    # Machine Learning & Data Science
    "Machine Learning": {"category": "Machine Learning & Data Science", "weight": 1.0, "aliases": ["machine learning", "ml", "machine-learning"]},
    "Deep Learning": {"category": "Machine Learning & Data Science", "weight": 1.0, "aliases": ["deep learning", "dl", "deep-learning", "neural networks"]},
    "NLP": {"category": "Machine Learning & Data Science", "weight": 1.0, "aliases": ["nlp", "natural language processing", "text mining", "computational linguistics"]},
    "Computer Vision": {"category": "Machine Learning & Data Science", "weight": 1.0, "aliases": ["computer vision", "cv", "image processing", "vision ai"]},
    "TensorFlow": {"category": "Machine Learning & Data Science", "weight": 0.9, "aliases": ["tensorflow", "tf", "tensorflow 2"]},
    "PyTorch": {"category": "Machine Learning & Data Science", "weight": 0.9, "aliases": ["pytorch", "torch"]},
    "Scikit-learn": {"category": "Machine Learning & Data Science", "weight": 0.9, "aliases": ["scikit-learn", "sklearn", "scikit learn"]},
    "Pandas": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["pandas", "pandas dataframe"]},
    "NumPy": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["numpy", "numpy array"]},
    "Statistics": {"category": "Machine Learning & Data Science", "weight": 0.9, "aliases": ["statistics", "statistical modeling", "hypothesis testing", "probability"]},
    "Data Visualization": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["data visualization", "data viz", "matplotlib", "seaborn", "plotly"]},
    "Feature Engineering": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["feature engineering", "feature extraction", "feature selection"]},
    "Model Evaluation": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["model evaluation", "validation metrics", "roc-auc", "cross-validation"]},
    "MLflow": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["mlflow", "mlflow tracking"]},
    "Keras": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["keras", "tf.keras"]},
    "OpenCV": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["opencv", "cv2"]},
    "Hugging Face": {"category": "Machine Learning & Data Science", "weight": 0.9, "aliases": ["hugging face", "huggingface", "transformers"]},
    "LLMs": {"category": "Machine Learning & Data Science", "weight": 1.0, "aliases": ["llm", "llms", "large language models", "generative ai", "genai"]},
    "LangChain": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["langchain", "langchain framework"]},
    "Time Series Analysis": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["time series", "time series analysis", "arima", "forecasting"]},
    "A/B Testing": {"category": "Machine Learning & Data Science", "weight": 0.8, "aliases": ["a/b testing", "ab testing", "split testing", "experimentation"]},

    # Web Development
    "HTML": {"category": "Web Development", "weight": 0.7, "aliases": ["html", "html5", "semantic html"]},
    "CSS": {"category": "Web Development", "weight": 0.7, "aliases": ["css", "css3", "vanilla css", "responsive css"]},
    "React": {"category": "Web Development", "weight": 1.0, "aliases": ["react", "react.js", "reactjs"]},
    "Angular": {"category": "Web Development", "weight": 0.9, "aliases": ["angular", "angular.js", "angularjs", "angular 14+"]},
    "Vue.js": {"category": "Web Development", "weight": 0.8, "aliases": ["vue", "vue.js", "vuejs", "vue 3"]},
    "Node.js": {"category": "Web Development", "weight": 1.0, "aliases": ["node.js", "node", "nodejs"]},
    "Express.js": {"category": "Web Development", "weight": 0.8, "aliases": ["express.js", "express", "expressjs"]},
    "Flask": {"category": "Web Development", "weight": 0.8, "aliases": ["flask", "flask framework", "flask api"]},
    "Django": {"category": "Web Development", "weight": 0.9, "aliases": ["django", "django rest framework", "drf"]},
    "FastAPI": {"category": "Web Development", "weight": 0.9, "aliases": ["fastapi", "fastapi framework"]},
    "REST APIs": {"category": "Web Development", "weight": 0.9, "aliases": ["rest api", "rest apis", "restful api", "restful web services", "rest"]},
    "GraphQL": {"category": "Web Development", "weight": 0.8, "aliases": ["graphql", "apollo graphql"]},
    "Next.js": {"category": "Web Development", "weight": 0.9, "aliases": ["next.js", "nextjs", "next"]},
    "Redux": {"category": "Web Development", "weight": 0.8, "aliases": ["redux", "redux toolkit", "rtk"]},
    "Tailwind CSS": {"category": "Web Development", "weight": 0.8, "aliases": ["tailwind css", "tailwind", "tailwindcss"]},
    "WebSockets": {"category": "Web Development", "weight": 0.8, "aliases": ["websockets", "websocket", "socket.io"]},

    # Databases
    "MySQL": {"category": "Databases", "weight": 0.9, "aliases": ["mysql", "mysql server", "mariadb"]},
    "PostgreSQL": {"category": "Databases", "weight": 1.0, "aliases": ["postgresql", "postgres", "pgsql"]},
    "SQLite": {"category": "Databases", "weight": 0.7, "aliases": ["sqlite", "sqlite3"]},
    "MongoDB": {"category": "Databases", "weight": 0.9, "aliases": ["mongodb", "mongo", "nosql mongodb"]},
    "Redis": {"category": "Databases", "weight": 0.8, "aliases": ["redis", "redis cache"]},
    "Cassandra": {"category": "Databases", "weight": 0.8, "aliases": ["cassandra", "apache cassandra"]},
    "ElasticSearch": {"category": "Databases", "weight": 0.8, "aliases": ["elasticsearch", "elastic search", "elk stack", "elk"]},
    "DynamoDB": {"category": "Databases", "weight": 0.8, "aliases": ["dynamodb", "aws dynamodb"]},
    "Database Design": {"category": "Databases", "weight": 0.9, "aliases": ["database design", "schema design", "normalization", "data modeling"]},
    "Indexing & Optimization": {"category": "Databases", "weight": 0.9, "aliases": ["indexing & optimization", "indexing", "query optimization", "query tuning", "db indexes"]},
    "ETL Pipelines": {"category": "Databases", "weight": 0.9, "aliases": ["etl pipelines", "etl", "extract transform load", "data pipelines", "data pipeline"]},

    # Cloud & DevOps
    "AWS": {"category": "Cloud & DevOps", "weight": 1.0, "aliases": ["aws", "amazon web services", "aws cloud"]},
    "Azure": {"category": "Cloud & DevOps", "weight": 0.9, "aliases": ["azure", "microsoft azure"]},
    "Google Cloud": {"category": "Cloud & DevOps", "weight": 0.9, "aliases": ["google cloud", "gcp", "google cloud platform"]},
    "Docker": {"category": "Cloud & DevOps", "weight": 1.0, "aliases": ["docker", "docker containers", "dockerfile"]},
    "Kubernetes": {"category": "Cloud & DevOps", "weight": 1.0, "aliases": ["kubernetes", "k8s"]},
    "Linux": {"category": "Cloud & DevOps", "weight": 0.9, "aliases": ["linux", "unix", "ubuntu", "centos", "rhel", "linux cli"]},
    "Git": {"category": "Cloud & DevOps", "weight": 0.9, "aliases": ["git", "git vcs", "version control"]},
    "GitHub": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["github", "github actions"]},
    "CI/CD": {"category": "Cloud & DevOps", "weight": 1.0, "aliases": ["ci/cd", "continuous integration", "continuous deployment", "jenkins pipeline", "cicd"]},
    "Terraform": {"category": "Cloud & DevOps", "weight": 0.9, "aliases": ["terraform", "infrastructure as code", "iac terraform"]},
    "Ansible": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["ansible", "ansible automation"]},
    "Jenkins": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["jenkins", "jenkins ci"]},
    "Prometheus": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["prometheus", "prometheus monitoring"]},
    "Grafana": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["grafana", "grafana dashboards"]},
    "Serverless": {"category": "Cloud & DevOps", "weight": 0.8, "aliases": ["serverless", "aws lambda", "cloud functions"]},

    # Cybersecurity
    "Network Security": {"category": "Cybersecurity", "weight": 1.0, "aliases": ["network security", "firewalls", "vpn", "network defense"]},
    "Ethical Hacking": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["ethical hacking", "white hat", "penetration testing", "pentesting"]},
    "OWASP": {"category": "Cybersecurity", "weight": 1.0, "aliases": ["owasp", "owasp top 10", "web application security"]},
    "SIEM": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["siem", "splunk", "qradar", "security information event management"]},
    "Vulnerability Assessment": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["vulnerability assessment", "nessus", "vulnerability scanning", "cve"]},
    "Cryptography": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["cryptography", "pki", "tls", "encryption", "hashing"]},
    "Incident Response": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["incident response", "threat containment", "dfir"]},
    "Identity and Access Management": {"category": "Cybersecurity", "weight": 0.9, "aliases": ["identity and access management", "iam", "rbac", "oauth", "saml"]},

    # Business & Analytics
    "Excel": {"category": "Business & Analytics", "weight": 0.8, "aliases": ["excel", "ms excel", "advanced excel", "vlookup", "pivot tables"]},
    "Power BI": {"category": "Business & Analytics", "weight": 1.0, "aliases": ["power bi", "powerbi", "dax"]},
    "Tableau": {"category": "Business & Analytics", "weight": 0.9, "aliases": ["tableau", "tableau desktop"]},
    "Business Intelligence": {"category": "Business & Analytics", "weight": 0.9, "aliases": ["business intelligence", "bi", "enterprise reporting"]},
    "Requirements Analysis": {"category": "Business & Analytics", "weight": 0.9, "aliases": ["requirements analysis", "brd", "functional specs", "user stories"]},
    "Communication": {"category": "Business & Analytics", "weight": 0.8, "aliases": ["communication", "stakeholder communication", "presentation skills"]},
    "Agile": {"category": "Business & Analytics", "weight": 0.8, "aliases": ["agile", "agile methodologies", "scrum", "sprints", "kanban"]},
    "Project Management": {"category": "Business & Analytics", "weight": 0.8, "aliases": ["project management", "jira", "scope management"]},
    "Data Storytelling": {"category": "Business & Analytics", "weight": 0.8, "aliases": ["data storytelling", "executive presentations", "kpi reporting"]},
}

class SkillExtractor:
    def __init__(self, taxonomy: Dict[str, Any] = None):
        self.taxonomy = taxonomy or DEFAULT_SKILL_TAXONOMY
        self._build_matchers()
        
    def _build_matchers(self):
        """Precompile boundary-aware regex matchers for each canonical skill and alias."""
        self.compiled_matchers: List[Tuple[str, re.Pattern, Dict[str, Any]]] = []
        
        # Sort skills by alias string length descending to match longest multiword phrases first
        alias_tuples = []
        for canonical_name, data in self.taxonomy.items():
            aliases = [canonical_name.lower()] + [a.lower() for a in data.get("aliases", [])]
            for alias in set(aliases):
                alias_tuples.append((alias, canonical_name, data))
                
        alias_tuples.sort(key=lambda x: len(x[0]), reverse=True)
        
        for alias, canonical_name, data in alias_tuples:
            escaped = re.escape(alias)
            # Use boundary matching that accommodates symbols like ++, #, .
            pattern_str = rf'(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_])'
            pattern = re.compile(pattern_str, re.IGNORECASE)
            self.compiled_matchers.append((alias, pattern, canonical_name, data))

    def extract_skills(self, text: str, section_name: str = "Full Document") -> List[Dict[str, Any]]:
        """
        Extract normalized skills from given text using boundary-aware NLP phrase matching.
        Returns a list of extracted skill dicts with canonical name, category, confidence, and weight.
        """
        if not text or not text.strip():
            return []
            
        found_skills: Dict[str, Dict[str, Any]] = {}
        
        # Perform boundary-aware matching
        for alias, pattern, canonical, data in self.compiled_matchers:
            if canonical in found_skills:
                continue
                
            matches = list(pattern.finditer(text))
            if matches:
                # Calculate confidence: higher for exact canonical match or in Skills section
                confidence = 1.0 if alias == canonical.lower() else 0.95
                if section_name.lower() in ["skills", "technical skills"]:
                    confidence = 1.0
                    
                found_skills[canonical] = {
                    "skill_name": canonical,
                    "category": data["category"],
                    "confidence": confidence,
                    "weight": data.get("weight", 1.0),
                    "source_section": section_name,
                    "is_confirmed": True
                }
                
        return list(found_skills.values())

    def extract_from_sections(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract skills across detected sections with section provenance."""
        combined_skills: Dict[str, Dict[str, Any]] = {}
        
        # Priority order of sections
        section_priority = ["Skills", "Projects", "Experience", "Summary", "Education", "Certifications", "Header"]
        
        for sec in section_priority:
            if sec in sections:
                extracted = self.extract_skills(sections[sec], section_name=sec)
                for item in extracted:
                    name = item["skill_name"]
                    if name not in combined_skills:
                        combined_skills[name] = item
                        
        # Any remaining sections
        for sec, content in sections.items():
            if sec not in section_priority:
                extracted = self.extract_skills(content, section_name=sec)
                for item in extracted:
                    name = item["skill_name"]
                    if name not in combined_skills:
                        combined_skills[name] = item
                        
        return list(combined_skills.values())

# Global singleton instance
skill_extractor = SkillExtractor()
