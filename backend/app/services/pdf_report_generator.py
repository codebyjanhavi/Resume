"""Generate downloadable PDF reports from resume analysis results."""

import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf_report(analysis_dict: dict) -> BytesIO:
    """
    Generates a PDF analysis report for SkillSight AI.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1e1b4b'),
        alignment=TA_LEFT
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_LEFT
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    
    story = []
    
    # Header Banner
    story.append(Paragraph("SKILLSIGHT AI — RESUME SKILL GAP AUDIT", title_style))
    created_date = analysis_dict.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    story.append(Paragraph(f"Autonomous Career Intelligence Report | Generated: {created_date}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366f1"), spaceBefore=8, spaceAfter=14))
    
    # Candidate & Role Overview Table
    candidate_name = analysis_dict.get("candidate_name") or "Candidate Profile"
    target_role = analysis_dict.get("target_role_title") or "General Assessment"
    predicted_role = analysis_dict.get("predicted_role") or "Unknown"
    confidence = analysis_dict.get("predicted_role_confidence", 0.0)
    
    meta_data = [
        [
            Paragraph("Candidate Reference:", meta_label),
            Paragraph(candidate_name, body_style),
            Paragraph("Target Role Evaluated:", meta_label),
            Paragraph(target_role, body_style)
        ],
        [
            Paragraph("Resume File:", meta_label),
            Paragraph(analysis_dict.get("resume_filename", "N/A"), body_style),
            Paragraph("ML Predicted Role:", meta_label),
            Paragraph(f"{predicted_role} ({confidence * 100:.1f}% conf)", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[120, 140, 130, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))
    
    # Core Metrics KPI Summary
    story.append(Paragraph("1. Compatibility & Competency Metrics", section_heading))
    mand_cov = analysis_dict.get("mandatory_skill_coverage", 0.0)
    over_cov = analysis_dict.get("overall_skill_coverage", 0.0)
    text_sim = analysis_dict.get("text_similarity_score", 0.0)
    
    kpi_data = [
        [
            Paragraph(f"<b>{mand_cov:.1f}%</b><br/><font size=7 color='#64748b'>Mandatory Skill Coverage</font>", body_style),
            Paragraph(f"<b>{over_cov:.1f}%</b><br/><font size=7 color='#64748b'>Overall Weighted Coverage</font>", body_style),
            Paragraph(f"<b>{text_sim:.1f}%</b><br/><font size=7 color='#64748b'>Text Similarity Score</font>", body_style)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[175, 175, 180])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))
    
    # Matched & Missing Skills Breakdown
    story.append(Paragraph("2. Skill Gap Breakdown", section_heading))
    matched_skills = [s["skill_name"] for s in analysis_dict.get("matched_skills", [])]
    missing_mand = [s["skill_name"] for s in analysis_dict.get("missing_mandatory_skills", [])]
    missing_pref = [s["skill_name"] for s in analysis_dict.get("missing_preferred_skills", [])]
    
    breakdown_data = [
        [
            Paragraph("<b>Status Category</b>", meta_label),
            Paragraph("<b>Identified Skills</b>", meta_label),
            Paragraph("<b>Count</b>", meta_label)
        ],
        [
            Paragraph("<font color='#059669'><b>Matched Skills</b></font>", body_style),
            Paragraph(", ".join(matched_skills) if matched_skills else "None", body_style),
            Paragraph(str(len(matched_skills)), body_style)
        ],
        [
            Paragraph("<font color='#dc2626'><b>Missing Mandatory</b></font>", body_style),
            Paragraph(", ".join(missing_mand) if missing_mand else "None (Complete)", body_style),
            Paragraph(str(len(missing_mand)), body_style)
        ],
        [
            Paragraph("<font color='#d97706'><b>Missing Preferred</b></font>", body_style),
            Paragraph(", ".join(missing_pref) if missing_pref else "None", body_style),
            Paragraph(str(len(missing_pref)), body_style)
        ]
    ]
    breakdown_table = Table(breakdown_data, colWidths=[130, 350, 50])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (2, 0), (2, -1), 'CENTER')
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 14))
    
    # Resume Improvement Suggestions
    suggestions = analysis_dict.get("suggestions", [])
    if suggestions:
        story.append(Paragraph("3. Heuristic Resume Improvement Recommendations", section_heading))
        for sug in suggestions[:4]:
            t_color = "#dc2626" if sug["type"] == "warning" else ("#059669" if sug["type"] == "strength" else "#2563eb")
            story.append(Paragraph(f"• <font color='{t_color}'><b>[{sug.get('category', 'General')}]</b> {sug.get('message', '')}</font>", body_style))
            story.append(Paragraph(f"  <font color='#64748b'>{sug.get('details', '')}</font>", body_style))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 10))
        
    # Academic Disclaimer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph(
        "Notice: This report was synthesized by SkillSight AI for career intelligence, skill gap analysis, and academic demonstration. "
        "Evaluations are computed via deterministic rule algorithms and machine learning models trained on synthetic benchmark datasets.",
        disclaimer_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
