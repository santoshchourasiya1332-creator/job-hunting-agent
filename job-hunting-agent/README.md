Autonomous Job-Hunting Agent & Production DevOps Pipeline
An end-to-end automated DevOps infrastructure and AI-driven agent designed to scan job descriptions, solve authentication barriers via automated OTP tracking, tailor resumes dynamically, and deploy cleanly onto a self-hosted Kubernetes cluster.

Architecture & Tech Stack
Cloud Infrastructure: AWS (Terraform-managed VPC, Subnets, Security Groups, and EC2 instances).
Container Orchestration: K3s Lightweight Kubernetes with automated node bootstrapping.
CI/CD Automation: GitLab CI/CD multi-stage pipeline (Terraform validation/apply, Docker multi-stage builds, and dynamic SSH deployment).
Observability: LGTM Stack (Loki, Grafana, Alloy) for container metrics and log tracking.
Agent Core: Python, Playwright (headless browser), Groq LLM API, Gmail IMAP (OTP extraction), and ReportLab (PDF tailoring).
Repository Structure
terraform/: Infrastructure-as-Code scripts and automated K3s user_data.sh bootstrapping.
k8s/: Kubernetes manifest files including namespaces, deployment configurations, and cronjobs.
lgtm/: Observability stack configuration maps for monitoring logs and metrics.
app/: Core automation logic (LLM matching, OTP reader, resume compiler, and entry orchestrator).
.gitlab-ci.yml: Complete end-to-end CI/CD automation definition.
