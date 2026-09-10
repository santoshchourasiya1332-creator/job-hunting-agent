from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_tailored_pdf(profile: dict, highlighted_skills: list, output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A2B4C")
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1A2B4C"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748")
    )

    story = []

    # Candidate Header Section
    story.append(Paragraph(profile["name"], title_style))
    contact_line = f"{profile['location']} | {profile['phone']} | {profile['email']}"
    story.append(Paragraph(contact_line, subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=8))

    # Professional Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    summary_text = (
        f"Results-driven L2 Production & Platform Support / DevOps Engineer with "
        f"{profile['experience_years']} years of hands-on experience maintaining cloud infrastructure, automating CI/CD pipelines, "
        f"and managing enterprise monitoring systems. Proven expertise in {', '.join(highlighted_skills[:5])}."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))

    # Core Competencies & Skills Section (Completed)
    story.append(Paragraph("TECHNICAL SKILLS", section_heading))
    skills_text = ", ".join(profile["skills"])
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 6))

    # Certifications Section
    story.append(Paragraph("CERTIFICATIONS", section_heading))
    certs_text = " | ".join(profile["certifications"])
    story.append(Paragraph(certs_text, body_style))

    doc.build(story)