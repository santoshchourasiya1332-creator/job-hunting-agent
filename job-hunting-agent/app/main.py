import os
import sys
import logging
from jd_analyzer import analyze_job_description
from otp_reader import fetch_latest_otp
from resume_tailor import generate_tailored_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MASTER_PROFILE = {
    "name": "Santosh Chourasiya",
    "email": "santoshchourasiya1332@gmail.com",
    "phone": "+91-7987951332",
    "location": "Pune, India",
    "experience_years": "3.5+",
    "current_role": "L2 Production & Platform Support / DevOps Engineer",
    "skills": [
        "Linux", "Bash", "SQL", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "Git", "Prometheus", "Grafana", "Azure Monitor",
        "ServiceNow", "Azure Data Factory", "AutoSys"
    ],
    "certifications": [
        "Azure Fundamentals (AZ-900)",
        "Azure AI Fundamentals",
        "OCI Foundations Associate"
    ]
}

def execute_job_hunting_workflow(job_title: str, job_description_text: str):
    logging.info(f"Starting analysis for role: {job_title}")

    match_result = analyze_job_description(job_description_text, MASTER_PROFILE["skills"])
    logging.info(f"Skill Match Score: {match_result['match_score']}%")

    if match_result["match_score"] < 80:
        logging.info("Match score below 80% threshold. Skipping application.")
        return

    logging.info("Match score >= 80%. Generating tailored resume PDF...")
    output_pdf_path = f"/tmp/{job_title.replace(' ', '_')}_Resume.pdf"
    generate_tailored_pdf(MASTER_PROFILE, match_result["matching_skills"], output_pdf_path)

    logging.info(f"Tailored resume saved at: {output_pdf_path}")
    logging.info("Proceeding to automated application workflow...")

if __name__ == "__main__":
    sample_jd = """
    We are looking for a DevOps & L2 Production Support Engineer with expertise in Linux,
    Docker, Kubernetes, Terraform, and Monitoring tools like Grafana and Azure Monitor.
    """
    execute_job_hunting_workflow("DevOps_Support_Engineer", sample_jd)