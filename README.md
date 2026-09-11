# Zero-Cost Autonomous Job-Hunting Agent Architecture

A fully automated, zero-cost, event-driven pipeline and infrastructure framework designed to search jobs, analyze job descriptions using free LLM APIs, verify login challenges via automated Gmail OTP reading, dynamically tailor PDF resumes, and submit applications. The entire architecture runs strictly within the parameters of the **AWS Free Tier**.

---

## **Architecture Overview & Workflow**

![Autonomous Agent Workflow](Run-agent-cluster-root.jpg)

---

## **System Architecture & Resource Optimization Strategy**

Deploying an autonomous, containerized job-hunting application alongside a complete telemetry stack within the strict limits of the AWS Free Tier requires an aggressively optimized infrastructure footprint. 
* **Compute Provisioning:** Uses a single AWS EC2 instance (`t3.micro` or `t2.micro` depending on regional availability) operating with 1 vCPU, 1 GB of physical RAM, and a 30 GB General Purpose SSD (`gp3`/`gp2`) root block device.
* **Control Plane:** Standard Kubernetes distributions and managed cloud options like Amazon EKS are prohibited due to resource overhead and hourly control plane costs. The system instead employs **Lightweight Kubernetes (K3s)**, stripped of heavy bundled controllers, to establish an enterprise-grade control plane that fits comfortably inside the available hardware constraints.
* **Memory Management & Swap Space:** Executing browser automation workflows alongside observability collection services on a single node with 1 GB of physical RAM introduces a significant risk of Out-Of-Memory (OOM) kernel termination events. To ensure continuous uptime without incurring AWS charges, the underlying operating system implements a kernel-level memory management architecture. A **2 GB dedicated swap space** is provisioned directly on the SSD root drive. The virtual memory subsystem of the Linux kernel is configured with `vm.swappiness=10` and `vm.vfs_cache_pressure=50`. Lowering swappiness ensures that active application processes remain in physical RAM while allowing transient execution bursts from ephemeral Playwright browser tasks to swap out idle memory pages seamlessly.
* **Ingress Routing:** To guarantee that total cluster RAM consumption remains strictly under the 900 MiB threshold, default packaged K3s components—specifically the Traefik Ingress Controller and ServiceLB—are explicitly disabled during node bootstrapping. Ingress routing is offloaded to a lightweight NGINX Ingress Controller operating on NodePort/HostPort interfaces, avoiding any dependency on paid AWS Application or Network Load Balancers.

---

## **Repository Structure**

```text
autonomous-job-agent/
├── .gitlab-ci.yml                 # Multi-stage pipeline definition for infrastructure, container, and cluster deployment
├── Dockerfile                     # Multi-stage container build definition
├── terraform/                     # Infrastructure-as-Code modules for AWS resource provision
│   ├── main.tf                    # Core AWS provider, network topology, security perimeter, and EC2 definitions
│   ├── variables.tf               # Input variable definitions and operational parameters
│   ├── outputs.tf                 # Exported infrastructure attributes and connection strings
│   └── user_data.sh               # Cloud-init shell automation for swap creation and K3s node setup
├── k8s/                           # Kubernetes Deployments & CronJobs
│   ├── namespace.yaml
│   ├── agent-cronjob.yaml
│   ├── playwright-deployment.yaml
│   └── ingress.yaml
├── lgtm/                          # Observability Stack Configuration
│   ├── values-loki.yaml           # Loki single-binary storage config
│   ├── values-alloy.yaml          # Grafana Alloy metric/log scrapers
│   └── values-grafana.yaml        # Visualizer settings
└── app/                           # Core Python Automation Scripts
    ├── main.py                    # Main workflow orchestrator
    ├── jd_analyzer.py             # Free LLM JD Matcher (Groq / Llama3)
    ├── otp_reader.py              # Automated Gmail IMAP OTP reader
    ├── resume_tailor.py           # ReportLab dynamic PDF resume generator
    └── requirements.txt           # Python dependencies