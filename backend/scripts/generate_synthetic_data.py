"""
Generate reproducible, fictional datasets used to seed and train SkillSight AI:
- 15 Tech Job Roles
- 5,250 Synthetic Resume Profiles
- 1,200 Synthetic Job Descriptions
- Role Skill Requirements & Weights
- Comprehensive Skills Taxonomy
"""

import json
import os
import random
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

# Seed for absolute reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

TARGET_ROLES = [
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "Python Developer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "Java Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Business Analyst",
    "Software Engineer",
    "AI Engineer",
    "Database Administrator",
]

# Master Taxonomy with category, aliases, and description
SKILL_TAXONOMY_DEF = [
    # Programming Languages
    ("Python", "Programming Languages", ["py", "python3"], 1.0),
    ("Java", "Programming Languages", ["core java", "java 17", "java 11", "java 8"], 1.0),
    ("JavaScript", "Programming Languages", ["js", "es6", "vanilla js"], 1.0),
    ("TypeScript", "Programming Languages", ["ts"], 1.0),
    ("C", "Programming Languages", ["c lang"], 0.8),
    ("C++", "Programming Languages", ["cpp", "cplusplus"], 0.9),
    ("C#", "Programming Languages", ["csharp", "c sharp", ".net c#"], 0.9),
    ("Kotlin", "Programming Languages", ["kotlin android"], 0.8),
    ("Go", "Programming Languages", ["golang"], 0.9),
    ("PHP", "Programming Languages", ["php7", "php8"], 0.7),
    ("SQL", "Programming Languages", ["structured query language", "ansi sql"], 1.0),
    ("R", "Programming Languages", ["r language", "rstats"], 0.8),
    ("Rust", "Programming Languages", ["rustlang"], 0.8),
    ("Scala", "Programming Languages", ["scala lang"], 0.8),
    ("Shell Scripting", "Programming Languages", ["bash", "sh", "zsh", "shell script"], 0.8),

    # Machine Learning & Data Science
    ("Machine Learning", "Machine Learning & Data Science", ["ml", "machine-learning"], 1.0),
    ("Deep Learning", "Machine Learning & Data Science", ["dl", "deep-learning", "neural networks"], 1.0),
    ("NLP", "Machine Learning & Data Science", ["natural language processing", "text mining"], 1.0),
    ("Computer Vision", "Machine Learning & Data Science", ["cv", "image processing", "vision ai"], 1.0),
    ("TensorFlow", "Machine Learning & Data Science", ["tf", "tensorflow 2"], 0.9),
    ("PyTorch", "Machine Learning & Data Science", ["torch"], 0.9),
    ("Scikit-learn", "Machine Learning & Data Science", ["sklearn", "scikit learn"], 0.9),
    ("Pandas", "Machine Learning & Data Science", ["pandas dataframe"], 0.8),
    ("NumPy", "Machine Learning & Data Science", ["numpy array"], 0.8),
    ("Statistics", "Machine Learning & Data Science", ["statistical modeling", "hypothesis testing"], 0.9),
    ("Data Visualization", "Machine Learning & Data Science", ["data viz", "matplotlib", "seaborn"], 0.8),
    ("Feature Engineering", "Machine Learning & Data Science", ["feature extraction", "feature selection"], 0.8),
    ("Model Evaluation", "Machine Learning & Data Science", ["validation metrics", "roc-auc", "cross-validation"], 0.8),
    ("MLflow", "Machine Learning & Data Science", ["mlflow tracking"], 0.8),
    ("Keras", "Machine Learning & Data Science", ["tf.keras"], 0.8),
    ("OpenCV", "Machine Learning & Data Science", ["computer vision cv2"], 0.8),
    ("Hugging Face", "Machine Learning & Data Science", ["transformers", "huggingface"], 0.9),
    ("LLMs", "Machine Learning & Data Science", ["large language models", "generative ai", "genai"], 1.0),
    ("LangChain", "Machine Learning & Data Science", ["langchain framework"], 0.8),
    ("Time Series Analysis", "Machine Learning & Data Science", ["arima", "forecasting"], 0.8),
    ("A/B Testing", "Machine Learning & Data Science", ["split testing", "experimentation"], 0.8),

    # Web Development
    ("HTML", "Web Development", ["html5", "semantic html"], 0.7),
    ("CSS", "Web Development", ["css3", "vanilla css", "responsive css"], 0.7),
    ("React", "Web Development", ["react.js", "reactjs"], 1.0),
    ("Angular", "Web Development", ["angular.js", "angularjs", "angular 14+"], 0.9),
    ("Vue.js", "Web Development", ["vue", "vuejs", "vue 3"], 0.8),
    ("Node.js", "Web Development", ["node", "nodejs"], 1.0),
    ("Express.js", "Web Development", ["express", "expressjs"], 0.8),
    ("Flask", "Web Development", ["flask framework", "flask api"], 0.8),
    ("Django", "Web Development", ["django rest framework", "drf"], 0.9),
    ("FastAPI", "Web Development", ["fastapi framework"], 0.9),
    ("REST APIs", "Web Development", ["restful api", "restful web services", "rest api"], 0.9),
    ("GraphQL", "Web Development", ["apollo graphql"], 0.8),
    ("Next.js", "Web Development", ["nextjs", "next"], 0.9),
    ("Redux", "Web Development", ["redux toolkit", "rtk"], 0.8),
    ("Tailwind CSS", "Web Development", ["tailwind", "tailwindcss"], 0.8),
    ("WebSockets", "Web Development", ["socket.io", "websocket"], 0.8),

    # Databases
    ("MySQL", "Databases", ["mysql server", "mariadb"], 0.9),
    ("PostgreSQL", "Databases", ["postgres", "pgsql"], 1.0),
    ("SQLite", "Databases", ["sqlite3"], 0.7),
    ("MongoDB", "Databases", ["mongo", "nosql mongodb"], 0.9),
    ("Redis", "Databases", ["redis cache"], 0.8),
    ("Cassandra", "Databases", ["apache cassandra"], 0.8),
    ("ElasticSearch", "Databases", ["elasticsearch", "elastic search", "elk"], 0.8),
    ("DynamoDB", "Databases", ["aws dynamodb"], 0.8),
    ("Database Design", "Databases", ["schema design", "normalization", "data modeling"], 0.9),
    ("Indexing & Optimization", "Databases", ["query optimization", "query tuning", "db indexes"], 0.9),
    ("ETL Pipelines", "Databases", ["etl", "extract transform load", "data pipelines"], 0.9),

    # Cloud & DevOps
    ("AWS", "Cloud & DevOps", ["amazon web services", "aws cloud"], 1.0),
    ("Azure", "Cloud & DevOps", ["microsoft azure"], 0.9),
    ("Google Cloud", "Cloud & DevOps", ["gcp", "google cloud platform"], 0.9),
    ("Docker", "Cloud & DevOps", ["docker containers", "dockerfile"], 1.0),
    ("Kubernetes", "Cloud & DevOps", ["k8s"], 1.0),
    ("Linux", "Cloud & DevOps", ["unix", "ubuntu", "centos", "rhel", "linux cli"], 0.9),
    ("Git", "Cloud & DevOps", ["git vcs", "version control"], 0.9),
    ("GitHub", "Cloud & DevOps", ["github actions"], 0.8),
    ("CI/CD", "Cloud & DevOps", ["continuous integration", "continuous deployment", "jenkins pipeline"], 1.0),
    ("Terraform", "Cloud & DevOps", ["infrastructure as code", "iac terraform"], 0.9),
    ("Ansible", "Cloud & DevOps", ["ansible automation"], 0.8),
    ("Jenkins", "Cloud & DevOps", ["jenkins ci"], 0.8),
    ("Prometheus", "Cloud & DevOps", ["prometheus monitoring"], 0.8),
    ("Grafana", "Cloud & DevOps", ["grafana dashboards"], 0.8),
    ("Serverless", "Cloud & DevOps", ["aws lambda", "cloud functions"], 0.8),

    # Cybersecurity
    ("Network Security", "Cybersecurity", ["firewalls", "vpn", "network defense"], 1.0),
    ("Ethical Hacking", "Cybersecurity", ["white hat", "penetration testing", "pentesting"], 0.9),
    ("OWASP", "Cybersecurity", ["owasp top 10", "web application security"], 1.0),
    ("SIEM", "Cybersecurity", ["splunk", "qradar", "security information event management"], 0.9),
    ("Vulnerability Assessment", "Cybersecurity", ["nessus", "vulnerability scanning", "cve"], 0.9),
    ("Cryptography", "Cybersecurity", ["pki", "tls", "encryption", "hashing"], 0.9),
    ("Incident Response", "Cybersecurity", ["ir", "threat containment", "dfir"], 0.9),
    ("Identity and Access Management", "Cybersecurity", ["iam", "rbac", "oauth", "saml"], 0.9),

    # Business & Analytics
    ("Excel", "Business & Analytics", ["ms excel", "advanced excel", "vlookup", "pivot tables"], 0.8),
    ("Power BI", "Business & Analytics", ["powerbi", "dax"], 1.0),
    ("Tableau", "Business & Analytics", ["tableau desktop"], 0.9),
    ("Business Intelligence", "Business & Analytics", ["bi", "enterprise reporting"], 0.9),
    ("Requirements Analysis", "Business & Analytics", ["brd", "functional specs", "user stories"], 0.9),
    ("Communication", "Business & Analytics", ["stakeholder communication", "presentation skills"], 0.8),
    ("Agile", "Business & Analytics", ["agile methodologies", "scrum", "sprints", "kanban"], 0.8),
    ("Project Management", "Business & Analytics", ["jira", "scope management"], 0.8),
    ("Data Storytelling", "Business & Analytics", ["executive presentations", "kpi reporting"], 0.8),
]

# Role skill specifications: mandatory vs preferred
ROLE_PROFILES = {
    "Data Scientist": {
        "mandatory": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy", "SQL"],
        "preferred": ["Deep Learning", "NLP", "Scikit-learn", "Data Visualization", "Feature Engineering", "A/B Testing", "Git"],
        "bonus": ["Docker", "AWS", "BigQuery", "PyTorch", "Tableau"],
        "description": "Applies statistical modeling, machine learning, and advanced algorithms to extract predictive insights from complex datasets.",
    },
    "Machine Learning Engineer": {
        "mandatory": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn", "Docker"],
        "preferred": ["MLflow", "Feature Engineering", "Model Evaluation", "Linux", "Git", "REST APIs", "SQL"],
        "bonus": ["Kubernetes", "AWS", "Hugging Face", "CI/CD", "C++"],
        "description": "Designs, trains, optimizes, and productionizes scalable machine learning systems and deep neural network models.",
    },
    "Data Analyst": {
        "mandatory": ["SQL", "Excel", "Data Visualization", "Power BI", "Tableau", "Statistics"],
        "preferred": ["Python", "Pandas", "Business Intelligence", "Communication", "Data Storytelling"],
        "bonus": ["A/B Testing", "ETL Pipelines", "Requirements Analysis", "MySQL"],
        "description": "Transforms structured data into business insights, dashboards, KPI tracking, and strategic analytical reports.",
    },
    "Python Developer": {
        "mandatory": ["Python", "Django", "Flask", "REST APIs", "SQL", "Git"],
        "preferred": ["FastAPI", "PostgreSQL", "Docker", "Linux", "Redis", "Unit Testing"],
        "bonus": ["Pandas", "Celery", "AWS", "CI/CD", "HTML", "CSS"],
        "description": "Builds high-performance backend systems, microservices, and automation pipelines using modern Python frameworks.",
    },
    "Full Stack Developer": {
        "mandatory": ["JavaScript", "TypeScript", "React", "Node.js", "REST APIs", "HTML", "CSS", "SQL"],
        "preferred": ["Express.js", "PostgreSQL", "MongoDB", "Git", "Docker", "Tailwind CSS"],
        "bonus": ["Next.js", "Redis", "AWS", "CI/CD", "GraphQL"],
        "description": "Develops end-to-end web applications encompassing interactive client interfaces, backend services, and relational databases.",
    },
    "Frontend Developer": {
        "mandatory": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "Tailwind CSS"],
        "preferred": ["Next.js", "Redux", "REST APIs", "Git", "Responsive Design", "Vue.js"],
        "bonus": ["GraphQL", "WebSockets", "Docker", "Jest", "Angular"],
        "description": "Crafts responsive, accessible, high-performance web user interfaces, component libraries, and client workflows.",
    },
    "Backend Developer": {
        "mandatory": ["Node.js", "REST APIs", "PostgreSQL", "SQL", "Docker", "Git", "Database Design"],
        "preferred": ["Express.js", "Redis", "Linux", "CI/CD", "Microservices", "Python"],
        "bonus": ["Kubernetes", "AWS", "GraphQL", "ElasticSearch", "WebSockets"],
        "description": "Architects resilient backend microservices, robust API endpoints, caching tiers, and secure database interactions.",
    },
    "Java Developer": {
        "mandatory": ["Java", "SQL", "REST APIs", "Git", "Database Design"],
        "preferred": ["Spring Boot", "PostgreSQL", "MySQL", "Docker", "Linux", "CI/CD"],
        "bonus": ["Microservices", "Kafka", "Kubernetes", "Redis", "AWS"],
        "description": "Engineers enterprise applications, robust multithreaded backend services, and scalable transactional architectures in Java.",
    },
    "DevOps Engineer": {
        "mandatory": ["Linux", "Docker", "Kubernetes", "CI/CD", "Git", "Shell Scripting", "AWS"],
        "preferred": ["Terraform", "Ansible", "Jenkins", "Prometheus", "Grafana", "Python"],
        "bonus": ["Azure", "Google Cloud", "Network Security", "Serverless", "ElasticSearch"],
        "description": "Automates build, deployment, monitoring, container orchestration, and continuous integration infrastructure pipelines.",
    },
    "Cloud Engineer": {
        "mandatory": ["AWS", "Azure", "Terraform", "Linux", "Docker", "Network Security"],
        "preferred": ["Google Cloud", "Kubernetes", "CI/CD", "Shell Scripting", "Serverless", "Git"],
        "bonus": ["Python", "IAM", "Prometheus", "Database Design", "Ansible"],
        "description": "Provisions, migrates, secures, and oversees multi-cloud infrastructure environments and cloud-native solutions.",
    },
    "Cybersecurity Analyst": {
        "mandatory": ["Network Security", "OWASP", "SIEM", "Vulnerability Assessment", "Cryptography", "Linux"],
        "preferred": ["Ethical Hacking", "Incident Response", "Identity and Access Management", "Shell Scripting", "Python"],
        "bonus": ["Firewall Configuration", "Wireshark", "Splunk", "AWS", "Penetration Testing"],
        "description": "Monitors systems, conducts vulnerability assessments, investigates security events, and enforces defensive standards.",
    },
    "Business Analyst": {
        "mandatory": ["Requirements Analysis", "Business Intelligence", "Excel", "Communication", "Agile", "SQL"],
        "preferred": ["Power BI", "Tableau", "Project Management", "Data Storytelling", "Stakeholder Management"],
        "bonus": ["Python", "Scrum", "Process Mapping", "Jira", "User Stories"],
        "description": "Translates organizational goals into technical requirements, bridges stakeholders, and validates software solutions.",
    },
    "Software Engineer": {
        "mandatory": ["Data Structures", "Algorithms", "Git", "REST APIs", "SQL", "Database Design"],
        "preferred": ["Python", "Java", "C++", "Docker", "Linux", "Unit Testing", "CI/CD"],
        "bonus": ["Microservices", "System Design", "AWS", "Redis", "TypeScript"],
        "description": "Builds robust, maintainable, scalable software solutions applying clean code principles and algorithmic efficiency.",
    },
    "AI Engineer": {
        "mandatory": ["Python", "Machine Learning", "Deep Learning", "LLMs", "NLP", "PyTorch"],
        "preferred": ["LangChain", "Hugging Face", "TensorFlow", "Docker", "REST APIs", "Git"],
        "bonus": ["Computer Vision", "Vector Databases", "MLflow", "AWS", "FastAPI"],
        "description": "Specializes in developing generative AI pipelines, LLM application integrations, and fine-tuning neural architectures.",
    },
    "Database Administrator": {
        "mandatory": ["SQL", "Database Design", "Indexing & Optimization", "PostgreSQL", "MySQL", "Linux"],
        "preferred": ["ETL Pipelines", "Redis", "MongoDB", "Shell Scripting", "Backup & Recovery"],
        "bonus": ["Cassandra", "Docker", "ElasticSearch", "AWS", "Python"],
        "description": "Manages database health, query optimization, high availability, backup restoration, and database cluster capacity.",
    },
}

# Fictional names generator
FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Sam", "Jamie", "Cameron", "Avery",
    "Logan", "Quinn", "Skyler", "Jesse", "Dakota", "Reese", "Rowan", "Finley", "Hayden", "Kendall",
    "Drew", "Sage", "Peyton", "Elliot", "Kai", "Devon", "Harper", "Rory", "Milan", "Parker",
    "Sasha", "River", "Emerson", "Shiloh", "Eden", "Amari", "Adrian", "Micah", "Blake", "Corey",
    "Chris", "Pat", "Terry", "Lee", "Dana", "Robin", "Francis", "Kelly", "Gerry", "Lynn"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

UNIVERSITIES = [
    "State University of Technology", "Apex Institute of Science", "Metro Polytechnic Institute",
    "National Technical University", "Pacific Coast University", "Continental Academy of Computing",
    "Global Institute of Engineering", "Central Science Academy", "Highland University"
]

DEGREES = [
    ("Bachelor of Science", "Computer Science"),
    ("Bachelor of Science", "Software Engineering"),
    ("Bachelor of Science", "Data Science & Analytics"),
    ("Bachelor of Science", "Information Technology"),
    ("Bachelor of Engineering", "Computer Engineering"),
    ("Master of Science", "Computer Science"),
    ("Master of Science", "Artificial Intelligence & Robotics"),
    ("Master of Science", "Data Science"),
    ("Master of Science", "Software Engineering"),
    ("Bachelor of Business Administration", "Information Systems"),
]

PROJECT_TEMPLATES = {
    "Data Scientist": [
        ("Predictive Customer Churn Pipeline", "Built an end-to-end churn prediction framework utilizing XGBoost and Scikit-learn, optimizing AUC to 0.89.", ["Python", "Scikit-learn", "Pandas", "SQL"]),
        ("Healthcare Readmission Analytics", "Modeled 100k+ clinical patient outcomes with logistic regression and survival analysis with 92% sensitivity.", ["Python", "Statistics", "Data Visualization", "NumPy"]),
        ("E-Commerce Demand Forecaster", "Developed seasonal time-series forecasting algorithms reducing inventory stockout rates by 18%.", ["Python", "Pandas", "Time Series Analysis", "SQL"]),
    ],
    "Machine Learning Engineer": [
        ("Distributed Neural Image Classifier", "Trained deep convolutional networks with PyTorch on ResNet architectures, serving predictions via TorchServe.", ["PyTorch", "Deep Learning", "Computer Vision", "Docker"]),
        ("Real-time Inference Microservice", "Containerized low-latency inference pipelines handling 500 RPS with sub-30ms p99 latency.", ["Python", "Docker", "REST APIs", "FastAPI"]),
        ("NLP Sentiment Intelligence Engine", "Fine-tuned transformer models for multi-class entity extraction and customer feedback sentiment parsing.", ["NLP", "PyTorch", "Hugging Face", "Machine Learning"]),
    ],
    "Data Analyst": [
        ("Executive Sales KPI Dashboard", "Designed interactive executive dashboards connecting ERP data to Power BI, tracking $12M revenue streams.", ["Power BI", "SQL", "Excel", "Data Visualization"]),
        ("Customer Segmentation Report", "Executed RFM segmentation queries and cohort retention analysis across 50,000 active accounts.", ["SQL", "Tableau", "Statistics", "Communication"]),
        ("Supply Chain Metric Automation", "Automated weekly reconciliation spreadsheets and reporting dashboards, eliminating 15 hours of manual entry.", ["Excel", "SQL", "Business Intelligence", "Power BI"]),
    ],
    "Python Developer": [
        ("Distributed Task Processing Engine", "Implemented asynchronous queue workers with Celery and Redis to process 2M records daily.", ["Python", "Redis", "PostgreSQL", "Docker"]),
        ("Secure Payment Gateway API", "Constructed RESTful financial checkout services with Django REST Framework and token validation.", ["Python", "Django", "REST APIs", "SQL"]),
        ("Automated Data Scraper & Aggregator", "Architected multithreaded web scrapers parsing 40+ vendor portals with automated schema validation.", ["Python", "Flask", "PostgreSQL", "Git"]),
    ],
    "Full Stack Developer": [
        ("Collaborative Task Workspace", "Built real-time kanban application using React, TypeScript, Node.js backend, and PostgreSQL database.", ["React", "TypeScript", "Node.js", "PostgreSQL", "Tailwind CSS"]),
        ("E-Commerce Marketplace Platform", "Engineered product catalog, shopping cart, and authenticated checkout workflow with Next.js and Express.", ["JavaScript", "React", "Node.js", "REST APIs", "HTML", "CSS"]),
        ("Subscription Management Portal", "Developed customer self-service portal integrating Stripe billing hooks and user role management.", ["TypeScript", "React", "Express.js", "SQL", "Docker"]),
    ],
    "Frontend Developer": [
        ("Design System Component Library", "Created accessible design token library in React and TypeScript with Storybook documentation.", ["React", "TypeScript", "HTML", "CSS", "Tailwind CSS"]),
        ("Real-time Financial Analytics Dashboard", "Crafted responsive charting interface rendering sub-second telemetry feeds with WebSockets.", ["React", "TypeScript", "Tailwind CSS", "REST APIs", "WebSockets"]),
        ("Mobile-first Responsive E-Commerce App", "Re-architected client bundle with code splitting, improving Core Web Vitals LCP by 45%.", ["JavaScript", "React", "HTML", "CSS", "Next.js"]),
    ],
    "Backend Developer": [
        ("High-Throughput Authentication Microservice", "Authored OAuth2/JWT auth service handling 10,000 active concurrent user sessions.", ["Node.js", "PostgreSQL", "Redis", "REST APIs", "Docker"]),
        ("Event-Driven Notification Broker", "Implemented scalable pub/sub message workers distributing SMS and email updates.", ["Node.js", "Express.js", "Database Design", "Docker", "Git"]),
        ("Inventory Management REST Engine", "Engineered transactional database procedures with ACID compliance across warehouse nodes.", ["PostgreSQL", "SQL", "REST APIs", "Database Design", "Linux"]),
    ],
    "Java Developer": [
        ("Banking Transaction Routing Core", "Implemented high-concurrency payment message router using Java concurrency primitives and Spring Boot.", ["Java", "SQL", "REST APIs", "Database Design"]),
        ("Enterprise Inventory Tracking System", "Constructed relational persistence mapping layer with Hibernate ORM and PostgreSQL database.", ["Java", "PostgreSQL", "REST APIs", "Git", "Linux"]),
        ("Microservice Health & Metrics Aggregator", "Integrated enterprise metrics logging and distributed tracing across 12 Java microservices.", ["Java", "Docker", "CI/CD", "SQL", "Linux"]),
    ],
    "DevOps Engineer": [
        ("Zero-Downtime Multi-Cluster CI/CD Pipeline", "Architected automated GitLab CI/CD workflows provisioning Kubernetes clusters with Helm.", ["Docker", "Kubernetes", "CI/CD", "Linux", "Git"]),
        ("Infrastructure as Code Cloud Migration", "Migrated on-premises workloads to AWS VPC using modularized Terraform configurations.", ["AWS", "Terraform", "Linux", "Shell Scripting"]),
        ("Enterprise Observability Stack", "Configured Prometheus metric scrape collectors and Grafana alert alerting rules covering 99.95% uptime.", ["Prometheus", "Grafana", "Linux", "Docker", "Shell Scripting"]),
    ],
    "Cloud Engineer": [
        ("Multi-Region AWS Disaster Recovery Architecture", "Configured cross-region S3 replication, Route53 failover, and automated RDS snapshots.", ["AWS", "Terraform", "Network Security", "Linux"]),
        ("Hybrid Cloud Network Interconnect", "Deployed secure IPsec VPN tunnels connecting corporate datacenters to Azure Virtual WAN.", ["Azure", "AWS", "Network Security", "Docker"]),
        ("Serverless Event Processing Pipeline", "Engineered event-driven pipeline parsing log files via AWS Lambda and S3 bucket triggers.", ["AWS", "Terraform", "Linux", "Git"]),
    ],
    "Cybersecurity Analyst": [
        ("Automated Vulnerability Scan Pipeline", "Established scheduled Nessus scanning and CVE tracking resolving 45 critical vulnerabilities.", ["Vulnerability Assessment", "Linux", "Network Security", "OWASP"]),
        ("SOC Incident Response Playbook & SIEM", "Constructed Splunk threat correlation rules detecting anomalous privilege escalations.", ["SIEM", "Incident Response", "Network Security", "Linux"]),
        ("Web Application Security Hardening", "Remediated OWASP Top 10 vulnerabilities including CSRF, SQLi, and IDOR on public endpoints.", ["OWASP", "Network Security", "Cryptography", "Ethical Hacking"]),
    ],
    "Business Analyst": [
        ("ERP Migration Business Requirements Document", "Gathered requirements from 8 department heads, authoring 120+ functional user stories and criteria.", ["Requirements Analysis", "Agile", "Communication", "Project Management"]),
        ("Commercial Sales Analytics Platform", "Synthesized regional revenue drivers and churn KPIs into executive Power BI visual decks.", ["Business Intelligence", "Power BI", "Excel", "Data Storytelling"]),
        ("Process Optimization & Automation Roadmap", "Mapped current-state operational workflows, reducing invoice reconciliation cycle by 4 business days.", ["Agile", "Excel", "SQL", "Communication"]),
    ],
    "Software Engineer": [
        ("Distributed Cache Synchronization Layer", "Built memory-efficient LRU caching client reducing database read pressure by 60%.", ["Data Structures", "Algorithms", "Python", "SQL", "Git"]),
        ("Scalable File Storage Service", "Designed chunked multipart file upload microservice with SHA256 checksum integrity checks.", ["REST APIs", "SQL", "Database Design", "Docker", "Git"]),
        ("Asynchronous Job Dispatch Framework", "Constructed thread-safe priority task execution pool with graceful shutdown mechanics.", ["Data Structures", "Algorithms", "Linux", "Git", "Unit Testing"]),
    ],
    "AI Engineer": [
        ("Enterprise RAG Knowledge Assistant", "Engineered retrieval-augmented generation assistant with LangChain, FAISS vector search, and Llama 3.", ["LLMs", "LangChain", "Python", "NLP", "Hugging Face"]),
        ("Fine-Tuned Domain LLM Evaluator", "Executed LoRA parameter-efficient fine-tuning on domain-specific datasets, evaluating BLEU and ROUGE.", ["Python", "PyTorch", "Hugging Face", "Deep Learning", "LLMs"]),
        ("Multimodal Vision-Language Search", "Built multimodal semantic search engine embedding product imagery and natural language descriptions.", ["Computer Vision", "Python", "Deep Learning", "Docker", "REST APIs"]),
    ],
    "Database Administrator": [
        ("High-Availability PostgreSQL Cluster Setup", "Configured streaming replication, Patroni failover, and PgBouncer connection pooling.", ["PostgreSQL", "Database Design", "Indexing & Optimization", "Linux", "SQL"]),
        ("Query Optimization & Index Tuning Overhaul", "Analyzed slow query logs, redesigned composite indexes, improving p95 query times by 75%.", ["Indexing & Optimization", "SQL", "MySQL", "Database Design"]),
        ("Automated Disaster Recovery & Backup Testing", "Built automated WAL archiving scripts with daily test restoration validation in isolated sandboxes.", ["Linux", "Shell Scripting", "PostgreSQL", "Backup & Recovery", "SQL"]),
    ],
}

CERTIFICATIONS_BY_CATEGORY = {
    "Machine Learning & Data Science": ["TensorFlow Developer Certificate", "AWS Certified Machine Learning - Specialty", "Databricks Certified Associate Data Scientist"],
    "Cloud & DevOps": ["AWS Certified Solutions Architect", "Certified Kubernetes Administrator (CKA)", "HashiCorp Certified: Terraform Associate"],
    "Cybersecurity": ["CompTIA Security+", "Certified Ethical Hacker (CEH)", "AWS Certified Security - Specialty"],
    "Databases": ["Oracle Certified Professional MySQL", "PostgreSQL Certified Associate", "MongoDB Certified Developer"],
    "Business & Analytics": ["Certified Scrum Master (CSM)", "Microsoft Certified: Power BI Data Analyst", "CBAP Certified Business Analysis Professional"],
    "General": ["AWS Certified Cloud Practitioner", "GitHub Foundations Certified", "Google Cloud Associate Cloud Engineer"],
}

def generate_fictional_person(idx: int) -> Dict[str, str]:
    first = FIRST_NAMES[idx % len(FIRST_NAMES)]
    last = LAST_NAMES[(idx // len(FIRST_NAMES)) % len(LAST_NAMES)]
    num = 100 + (idx % 900)
    email = f"{first.lower()}.{last.lower()}{num}@fictional-domain.org"
    phone = f"+1-555-01{idx % 100:02d}"
    return {
        "name": f"{first} {last}",
        "email": email,
        "phone": phone
    }

def generate_resume_profile(record_id: int, target_role: str) -> Dict:
    person = generate_fictional_person(record_id)
    profile = ROLE_PROFILES[target_role]
    
    # Realistic experience: 0 to 12 years with weighted distribution
    exp_years = int(np.random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12], p=[0.05, 0.1, 0.15, 0.18, 0.17, 0.12, 0.08, 0.06, 0.04, 0.03, 0.02]))
    
    # Skills sampling: Include most mandatory skills + subset of preferred + some cross-role skills
    num_mandatory = random.randint(len(profile["mandatory"]) - 1, len(profile["mandatory"]))
    chosen_mandatory = random.sample(profile["mandatory"], min(num_mandatory, len(profile["mandatory"])))
    
    num_pref = random.randint(2, min(5, len(profile["preferred"])))
    chosen_pref = random.sample(profile["preferred"], num_pref)
    
    # 30% chance of 1-2 bonus or cross-domain skills (e.g. data scientist who knows React or Docker)
    chosen_other = []
    if random.random() < 0.6 and profile["bonus"]:
        chosen_other = random.sample(profile["bonus"], min(2, len(profile["bonus"])))
        
    all_skills = list(dict.fromkeys(chosen_mandatory + chosen_pref + chosen_other))
    
    # Education
    deg_title, deg_field = random.choice(DEGREES)
    uni = random.choice(UNIVERSITIES)
    grad_year = 2024 - exp_years
    
    # Projects
    available_projects = PROJECT_TEMPLATES.get(target_role, [])
    chosen_projects = random.sample(available_projects, min(2, len(available_projects)))
    
    # Certifications
    certs = []
    if exp_years >= 2 and random.random() < 0.6:
        cert_cat = random.choice(list(CERTIFICATIONS_BY_CATEGORY.keys()))
        certs.append(random.choice(CERTIFICATIONS_BY_CATEGORY[cert_cat]))
        
    # Build realistic resume text with structured sections
    resume_text_lines = [
        f"{person['name'].upper()} - SYNTHETIC PROFILE",
        f"Email: {person['email']} | Phone: {person['phone']} | Fictional Candidate ID: SYNTH-{record_id:05d}",
        "",
        "PROFESSIONAL SUMMARY",
        f"Dedicated {target_role} with {exp_years} years of experience designing and executing technical solutions. "
        f"Skilled in {', '.join(all_skills[:4])}. Proven track record delivering robust systems and measurable business impact.",
        "",
        "CORE TECHNICAL SKILLS",
        f"Technologies & Methodologies: {', '.join(all_skills)}",
        "",
        "WORK EXPERIENCE",
    ]
    
    if exp_years == 0:
        resume_text_lines.extend([
            f"Associate {target_role} Intern | Acme Tech Solutions Inc. | 2023 - 2024",
            f"- Supported senior engineers in maintaining codebases using {', '.join(all_skills[:3])}.",
            f"- Participated in agile sprint ceremonies, code reviews, and automated testing suites.",
            f"- Documented standard operating procedures and technical architecture guidelines."
        ])
    else:
        roles_count = 1 if exp_years <= 3 else 2
        comp_names = ["Apex Innovations", "Summit Cloud Dynamics", "Horizon Digital Labs"]
        for r_i in range(roles_count):
            c_name = comp_names[r_i]
            title = target_role if r_i == 0 else f"Junior {target_role}"
            years_span = f"{2024 - exp_years + (r_i*2)} - {2024 if r_i == 0 else 2024 - 2}"
            resume_text_lines.extend([
                f"{title} | {c_name} | {years_span}",
                f"- Architected and deployed scalable systems utilizing {', '.join(all_skills[r_i*2:r_i*2+4])}.",
                f"- Partnered with cross-functional teams to elevate operational efficiency and eliminate technical debt.",
                f"- Delivered solutions achieving 99.9% uptime and streamlined delivery pipelines."
            ])
            
    resume_text_lines.extend([
        "",
        "KEY PROJECTS",
    ])
    for p_title, p_desc, p_skills in chosen_projects:
        resume_text_lines.append(f"{p_title}:")
        resume_text_lines.append(f"- {p_desc} (Technologies: {', '.join(p_skills)})")
        
    resume_text_lines.extend([
        "",
        "EDUCATION",
        f"{deg_title} in {deg_field} | {uni} | Graduated {grad_year}",
    ])
    
    if certs:
        resume_text_lines.extend([
            "",
            "CERTIFICATIONS",
            f"{', '.join(certs)}"
        ])

    full_resume_text = "\n".join(resume_text_lines)
    
    return {
        "candidate_id": f"SYNTH-{record_id:05d}",
        "full_name": person["name"],
        "email": person["email"],
        "phone": person["phone"],
        "target_role": target_role,
        "years_experience": exp_years,
        "degree": deg_title,
        "field_of_study": deg_field,
        "university": uni,
        "skills_list": ";".join(all_skills),
        "certifications": ";".join(certs),
        "projects_count": len(chosen_projects),
        "resume_text": full_resume_text,
        "is_synthetic": True,
    }

def generate_job_description(record_id: int, role: str) -> Dict:
    profile = ROLE_PROFILES[role]
    comp_names = ["Nexus Global", "Starlight Systems", "Pinnacle Dynamics", "BlueWave Analytics", "Vanguard Cloud"]
    company = random.choice(comp_names)
    exp_req = random.choice(["1-3 years", "3-5 years", "5+ years", "2-4 years"])
    
    # Required skills (mandatory) and preferred skills
    req_skills = profile["mandatory"].copy()
    pref_skills = profile["preferred"][:random.randint(3, len(profile["preferred"]))]
    
    jd_lines = [
        f"JOB TITLE: {role}",
        f"COMPANY: {company} (Fictional Organization)",
        f"LOCATION: Remote / Hybrid | EXPERIENCE REQUIRED: {exp_req}",
        "",
        "ABOUT THE ROLE:",
        profile["description"],
        f"At {company}, we are seeking a qualified {role} to strengthen our technical division.",
        "",
        "CORE RESPONSIBILITIES:",
        f"- Design, build, and support production systems according to industry best practices.",
        f"- Work alongside cross-functional partners, data teams, and product managers.",
        f"- Maintain high availability, code quality, and security standards.",
        f"- Write well-tested, maintainable code using {', '.join(req_skills[:3])}.",
        "",
        "MANDATORY QUALIFICATIONS:",
        f"- Demonstrated competency in: {', '.join(req_skills)}.",
        f"- Hands-on proficiency solving complex engineering and architecture challenges.",
        f"- Relevant Bachelor's or Master's degree or equivalent practical experience.",
        "",
        "PREFERRED QUALIFICATIONS:",
        f"- Familiarity with: {', '.join(pref_skills)}.",
        f"- Experience operating in agile environments and modern cloud architectures.",
        "",
        "BENEFITS:",
        "- Competitive fictional compensation package, remote flexibility, and learning stipends."
    ]
    
    return {
        "job_id": f"JD-{record_id:04d}",
        "role_title": role,
        "company": company,
        "experience_level": exp_req,
        "mandatory_skills": ";".join(req_skills),
        "preferred_skills": ";".join(pref_skills),
        "description_text": "\n".join(jd_lines),
        "is_synthetic": True,
    }

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "synthetic"))
    os.makedirs(base_dir, exist_ok=True)
    
    print(f"[1/5] Generating master Skill Taxonomy ({len(SKILL_TAXONOMY_DEF)} skills)...")
    taxonomy_rows = []
    for skill_name, cat, aliases, weight in SKILL_TAXONOMY_DEF:
        taxonomy_rows.append({
            "skill_name": skill_name,
            "category": cat,
            "aliases": ";".join(aliases),
            "weight": weight
        })
    df_taxonomy = pd.DataFrame(taxonomy_rows)
    taxonomy_path = os.path.join(base_dir, "skills_taxonomy.csv")
    df_taxonomy.to_csv(taxonomy_path, index=False)
    
    print(f"[2/5] Generating Role Skill Requirements for {len(TARGET_ROLES)} roles...")
    req_rows = []
    for role, prof in ROLE_PROFILES.items():
        for s in prof["mandatory"]:
            req_rows.append({
                "role_title": role,
                "skill_name": s,
                "requirement_type": "mandatory",
                "importance_weight": 1.0,
                "role_description": prof["description"]
            })
        for s in prof["preferred"]:
            req_rows.append({
                "role_title": role,
                "skill_name": s,
                "requirement_type": "preferred",
                "importance_weight": 0.6,
                "role_description": prof["description"]
            })
    df_reqs = pd.DataFrame(req_rows)
    reqs_path = os.path.join(base_dir, "role_skill_requirements.csv")
    df_reqs.to_csv(reqs_path, index=False)
    
    # 350 samples per role * 15 roles = 5,250 synthetic resumes
    samples_per_role = 350
    total_resumes = samples_per_role * len(TARGET_ROLES)
    print(f"[3/5] Generating {total_resumes} synthetic candidate resumes (350 per role)...")
    
    resume_records = []
    curr_id = 1
    for role in TARGET_ROLES:
        for _ in range(samples_per_role):
            resume_records.append(generate_resume_profile(curr_id, role))
            curr_id += 1
            
    # Shuffle for realistic distribution
    random.shuffle(resume_records)
    df_resumes = pd.DataFrame(resume_records)
    resumes_path = os.path.join(base_dir, "synthetic_resumes.csv")
    df_resumes.to_csv(resumes_path, index=False)
    
    # 80 job descriptions per role * 15 roles = 1,200 synthetic job descriptions
    jds_per_role = 80
    total_jds = jds_per_role * len(TARGET_ROLES)
    print(f"[4/5] Generating {total_jds} synthetic job descriptions (80 per role)...")
    
    jd_records = []
    curr_jd_id = 1
    for role in TARGET_ROLES:
        for _ in range(jds_per_role):
            jd_records.append(generate_job_description(curr_jd_id, role))
            curr_jd_id += 1
            
    random.shuffle(jd_records)
    df_jds = pd.DataFrame(jd_records)
    jds_path = os.path.join(base_dir, "synthetic_job_descriptions.csv")
    df_jds.to_csv(jds_path, index=False)
    
    print("[5/5] Generating metadata manifest...")
    metadata = {
        "dataset_name": "SkillSight AI Synthetic Benchmark Dataset",
        "version": "1.0.0",
        "random_seed": RANDOM_SEED,
        "is_synthetic": True,
        "data_notice": "ALL DATA IN THIS DATASET IS COMPLETELY SYNTHETIC AND PROCEDURALLY GENERATED. NO REAL INDIVIDUALS, PROFILES, OR RESUMES ARE USED.",
        "roles_count": len(TARGET_ROLES),
        "target_roles": TARGET_ROLES,
        "total_resumes": len(df_resumes),
        "resumes_per_role": samples_per_role,
        "total_job_descriptions": len(df_jds),
        "jds_per_role": jds_per_role,
        "total_taxonomy_skills": len(df_taxonomy),
        "files": {
            "synthetic_resumes": "synthetic_resumes.csv",
            "synthetic_job_descriptions": "synthetic_job_descriptions.csv",
            "role_skill_requirements": "role_skill_requirements.csv",
            "skills_taxonomy": "skills_taxonomy.csv"
        }
    }
    meta_path = os.path.join(base_dir, "synthetic_dataset_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    print("\n[SUCCESS] Synthetic dataset generated successfully:")
    print(f"  - Resumes: {len(df_resumes)} records -> {resumes_path}")
    print(f"  - JDs: {len(df_jds)} records -> {jds_path}")
    print(f"  - Role Reqs: {len(df_reqs)} records -> {reqs_path}")
    print(f"  - Taxonomy: {len(df_taxonomy)} skills -> {taxonomy_path}")
    print(f"  - Metadata -> {meta_path}")

if __name__ == "__main__":
    main()
