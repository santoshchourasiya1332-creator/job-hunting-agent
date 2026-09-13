cd ~/ai_job_hunt-project && cat << 'EOF' > SETUP_GUIDE.md
# AI Job Hunt Project - Setup & Deployment Guide

This guide provides complete instructions to set up, build, configure, and deploy the AI Job Hunt Project either locally or on a cloud (AWS EC2 + Kubernetes/K3s) environment.

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Project Structure Overview](#2-project-structure-overview)
3. [Environment Secrets Configuration](#3-environment-secrets-configuration)
4. [Local Development & Testing with Docker](#4-local-development--testing-with-docker)
5. [Kubernetes & K3s Deployment (AWS EC2)](#5-kubernetes--k3s-deployment-aws-ec2)
6. [CI/CD Pipeline Setup (GitLab)](#6-cicd-pipeline-setup-gitlab)

---

## 1. Prerequisites
Make sure you have the following installed on your system or deployment server:
* Docker (v24.0+)
* Kubernetes CLI (`kubectl`)
* Helm (optional, for cluster package management)
* Terraform (v1.6+) — if provisioning cloud infrastructure via Terraform.
* Git

---

## 2. Project Structure Overview
Ensure your project files are organized as follows:
```text
ai_job_hunt-project/
├── app/
│   ├── main.py
│   ├── jd_analyzer.py          # Contains LLM logic (Groq / OpenAI configuration)
│   └── requirements.python     # Python dependencies
├── k8s/
│   ├── namespace.yaml
│   ├── ingress.yaml
│   ├── playwright-deployment.yaml
│   └── agent-cronjob.yaml      # Kubernetes CronJob specification
├── terraform/                  # Terraform configuration for AWS EC2/K3s
├── Dockerfile                  # Root-level Dockerfile for building the app
└── .gitlab-ci.yml              # GitLab CI/CD pipeline configuration

3. Environment Secrets Configuration
The project requires sensitive keys (Gmail credentials and Groq API key) to function. Do not hardcode these values.

Step-by-Step Secret Setup:
Create a secure environment file named secret.env in the root directory:

Bash
nano secret.env
Add your credentials in the exact format below (avoid shell-escaping issues by using a file):

Code snippet
GMAIL_USER_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
GROQ_API_KEY=your-groq-api-key
Save and exit the editor (Ctrl + O, Enter, Ctrl + X).

Apply these secrets into your Kubernetes cluster (job-agent namespace):

Bash
kubectl create secret generic agent-secrets --namespace=job-agent --from-env-file=secret.env --dry-run=client -o yaml | kubectl apply --validate=false -f -
Clean up the local environment file for security:

Bash
rm secret.env
4. Local Development & Testing with Docker
If you want to build and test the Docker container locally:

Navigate to the project root directory:

Bash
cd ~/ai_job_hunt-project
Build the Docker image:

Bash
docker build -t [registry.gitlab.com/ai_job_hunt-group/ai_job_hunt-project:latest](https://registry.gitlab.com/ai_job_hunt-group/ai_job_hunt-project:latest) .
Run the container locally (passing environment variables):

Bash
docker run --rm \
  -e GMAIL_USER_EMAIL="your-email@gmail.com" \
  -e GMAIL_APP_PASSWORD="your-password" \
  -e GROQ_API_KEY="your-groq-key" \
  [registry.gitlab.com/ai_job_hunt-group/ai_job_hunt-project:latest](https://registry.gitlab.com/ai_job_hunt-group/ai_job_hunt-project:latest)
5. Kubernetes & K3s Deployment (AWS EC2)
If you are managing deployments directly on an AWS EC2 instance running K3s:

Ensure K3s configuration is loaded:

Bash
mkdir -p ~/.kube
sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config
chmod 600 ~/.kube/config
Apply Kubernetes Manifests:

Bash
kubectl apply --validate=false -f k8s/namespace.yaml
kubectl apply --validate=false -f k8s/ingress.yaml
kubectl apply --validate=false -f k8s/playwright-deployment.yaml
kubectl apply --validate=false -f k8s/agent-cronjob.yaml
Run a Manual Test Job:
To trigger an immediate execution test from the CronJob template:

Bash
kubectl delete job final-test-run-new -n job-agent --ignore-not-found=true
kubectl create job --from=cronjob/job-hunting-agent-cron final-test-run-new -n job-agent
Check Logs:

Bash
kubectl logs -l batch.kubernetes.io/job-name=final-test-run-new -n job-agent --tail=50
6. CI/CD Pipeline Setup (GitLab)
To enable automated deployments via GitLab CI/CD:

Configure GitLab Project Variables:
Go to your GitLab Repository -> Settings > CI/CD > Variables and add:

SSH_PRIVATE_KEY (Your EC2 private key contents)

GMAIL_USER_EMAIL

GMAIL_APP_PASSWORD

GROQ_API_KEY

Trigger the Pipeline:
Commit and push your changes to the main branch:

Bash
git add .
git commit -m "chore: setup complete configuration and model updates"
git push origin main
Track the pipeline execution under GitLab > CI/CD > Pipelines.
EOF