# Autonomous AI Job-Hunting Agent & Production DevOps Pipeline

A production-grade, fully automated infrastructure and AI-driven pipeline designed to autonomously track job postings, solve multi-factor authentication barriers via real-time IMAP OTP retrieval, dynamically tailor professional resumes using LLMs, and deploy seamlessly onto a self-hosted Kubernetes cluster.

## Core Capabilities
* **AI-Powered Analysis & Customization:** Leverages Groq LLMs to analyze target job descriptions and compiles tailored PDF resumes using ReportLab.
* **Automated Authentication Handling:** Integrates headless browser automation via Playwright alongside secure IMAP mail parsing to handle login challenges and automated OTP verification.
* **Infrastructure-as-Code (IaC):** Provisions cloud infrastructure dynamically using Terraform for secure VPC subnets and EC2 node management on AWS.
* **Lightweight Kubernetes Orchestration:** Bootstraps a production-ready K3s cluster via automated node initialization scripts (`user_data.sh`).
* **Zero-Trust CI/CD Automation:** Orchestrated via GitLab CI/CD with secure runtime secret injection (`kubectl create secret`) preventing any hardcoded credentials.
* **Comprehensive Observability:** Configured with the LGTM stack (Loki, Grafana, Alloy) for robust container metrics tracking and centralized log aggregation.

## Tech Stack
* **Cloud & DevOps:** AWS, Terraform, K3s, GitLab CI/CD, Docker
* **Observability:** Loki, Grafana, Alloy (LGTM Stack)
* **Application Core:** Python, Playwright, Groq LLM API, Gmail IMAP, ReportLab
