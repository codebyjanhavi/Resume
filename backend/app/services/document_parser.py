"""Extract readable text, contact details, and sections from uploaded resumes."""

import os
import re
from typing import Dict, Any, Tuple
from pathlib import Path

# Safe extraction of text from documents
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text_parts = []
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text.strip())
        doc.close()
        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            return "[NOTICE: Document appears to be an image-only or scanned PDF. Text cannot be extracted without optical character recognition (OCR).]"
        return full_text
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    paragraphs.append(" | ".join(row_text))
                    
        full_text = "\n\n".join(paragraphs).strip()
        if not full_text:
            raise ValueError("DOCX document contains no readable text.")
        return full_text
    except Exception as e:
        raise ValueError(f"Error reading DOCX file: {str(e)}")

def extract_text_from_file(file_path: str, filename: str) -> str:
    """Detect file type and extract clean plain text."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif ext in [".txt"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported formats: PDF, DOCX, TXT.")

# Resume contact & section detection
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b')

SECTION_PATTERNS = {
    "Summary": [r"\b(summary|professional summary|profile|objective|career objective|about me)\b"],
    "Skills": [r"\b(skills|technical skills|core competencies|technologies|tools & technologies|expertise)\b"],
    "Experience": [r"\b(experience|work experience|employment history|professional experience|work history)\b"],
    "Projects": [r"\b(projects|key projects|academic projects|personal projects|featured projects)\b"],
    "Education": [r"\b(education|academic background|qualifications|academic credentials)\b"],
    "Certifications": [r"\b(certifications|licenses|courses|accreditations|certificates)\b"]
}

def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract candidate email, phone, and name heuristics without retaining external PII."""
    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0) if email_match else None
    
    phone_match = PHONE_REGEX.search(text)
    phone = phone_match.group(0) if phone_match else None
    
    # Candidate name heuristic: First non-empty line of the resume that doesn't look like an email or heading
    candidate_name = None
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:
        if "@" in line or "resume" in line.lower() or "curriculum" in line.lower() or "http" in line.lower():
            continue
        # Clean line of symbols
        cleaned = re.sub(r'[^a-zA-Z\s]', '', line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            candidate_name = cleaned
            break
            
    if not candidate_name and lines:
        first_line = lines[0].split("|")[0].split("-")[0].strip()
        candidate_name = first_line[:50]
        
    return {
        "candidate_name": candidate_name or "Candidate Profile",
        "email": email,
        "phone": phone
    }

def detect_sections(text: str) -> Dict[str, str]:
    """Segment resume text into standard sections (Summary, Skills, Experience, Projects, Education, Certifications)."""
    lines = text.split("\n")
    sections: Dict[str, list] = {}
    current_section = "Header"
    sections[current_section] = []
    
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        matched_section_name = None
        for sec_name, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                # Check if the line is short enough to be a section header and matches pattern
                if len(cleaned_line.split()) <= 5 and re.search(pat, cleaned_line, re.IGNORECASE):
                    matched_section_name = sec_name
                    break
            if matched_section_name:
                break
                
        if matched_section_name:
            current_section = matched_section_name
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(cleaned_line)
            
    # Join section text
    return {k: "\n".join(v).strip() for k, v in sections.items() if v}
