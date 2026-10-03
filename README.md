# Project 4 — End-to-End DevOps CI/CD Capstone

Automated pipeline for a Dockerized web app on **AWS EKS**, orchestrated by **Jenkins**: infrastructure (Terraform), configuration (Ansible), deployment (Kubernetes), and observability (Prometheus/Grafana).

| Evaluation (per [docs/task.md](docs/task.md)) | Weight |
|-----------------------------------------------|--------|
| Implementation | 75% |
| Documentation | 15% |
| Cost optimization | 10% |

**Region:** `ap-south-1` · **Requirements:** [docs/task.md](docs/task.md)

---

## Architecture

```
Developer --push--> GitHub --webhook/poll--> Jenkins (EC2)
                                                 |
        ------------------------------------------------------------------
        |              |              |              |                 |
   Test/Build/ECR   Terraform      Ansible        Deploy          Monitoring
        |          (VPC/EKS/S3)    (host cfg)    (kubectl)      (Prom/Grafana)
        v                                                            |
      ECR ----------------------------------------------------> EKS pods
```

Network, IAM, and components: [docs/architecture.md](docs/architecture.md).

---

## Project goals (task mapping)

| Goal | Delivery | Documentation |
|------|----------|---------------|
| Architecture (LB, orchestration, monitoring) | VPC, EKS, LoadBalancer Service, Prometheus/Grafana | [architecture.md](docs/architecture.md) |
| Terraform (VPC, subnets, EKS, S3 state) | `terraform/` + Jenkins Terraform stages | [terraform.md](docs/terraform.md) |
| Ansible configuration | `ansible/` runs after Terraform | [ansible.md](docs/ansible.md) |
| App on EKS (scale, resilience) | `kubernetes/` — probes, HPA | [kubernetes.md](docs/kubernetes.md) |
| Jenkins CI/CD | [jenkins/Jenkinsfile](jenkins/Jenkinsfile) | [pipeline.md](docs/pipeline.md) |
| Prometheus & Grafana | `monitoring/` — app + node metrics | [monitoring.md](docs/monitoring.md) |

---

## Jenkins pipeline

Single declarative pipeline: [jenkins/Jenkinsfile](jenkins/Jenkinsfile).

| Capstone stage ([task.md](docs/task.md)) | Jenkins stages |
|------------------------------------------|----------------|
| **1. Build** | Test → Build image → Push to ECR |
| **2. Infrastructure** | Terraform Init → Plan → Apply (includes `terraform validate`) |
| **3. Configuration** | Ansible Configure |
| **4. Deployment** | Deploy → Post-deploy smoke test |
| **5. Test & monitor** | Monitoring → Pipeline validation |

**Trigger:** Git push or SCM poll every 15 minutes — [jenkins-triggers.md](docs/jenkins-triggers.md).

```
Checkout → Terraform → Ansible → Test → Build → ECR → Deploy → Smoke → Monitoring → Validation
```

---

## Repository layout

```
app/           # Flask app, Dockerfile, pytest
terraform/     # VPC, EKS, S3 backend, IAM
ansible/       # Playbooks (Jenkins CI host)
jenkins/       # Jenkinsfile
kubernetes/    # Deployment, Service, HPA
monitoring/    # Prometheus, Grafana, kube-state-metrics, node-exporter
docs/          # Runbooks, sprint logs, task requirements
```

---

## Sprint summary

| Sprint | Topic | Log |
|--------|--------|-----|
| 1 | Docker, ECR, Jenkins on EC2 | [sprint-1.md](docs/sprint-1.md) |
| 2 | Terraform + remote state + Jenkins | [terraform.md](docs/terraform.md) |
| 3 | Ansible after Terraform | [ansible.md](docs/ansible.md) |
| 4 | Deploy to EKS (LB, HPA, smoke test) | [pipeline.md](docs/pipeline.md) |
| 5 | Prometheus, Grafana, alerts | [monitoring.md](docs/monitoring.md) |
| 6 | E2E tests, cost doc, demo script | [sprint-6.md](docs/sprint-6.md) |

Evidence screenshots: add PNGs per [docs/screenshots/README.md](docs/screenshots/README.md).

---

## Step-by-step — run the project

### Prerequisites

- AWS account (EKS, ECR, VPC, S3, DynamoDB)
- Jenkins on EC2 with **Pipeline from SCM**, script path `jenkins/Jenkinsfile`, branch `*/main`
- ECR repository `devops-capstone-app` and Terraform S3 backend (see [terraform.md](docs/terraform.md))
- Jenkins setup and access: [sprint-1.md](docs/sprint-1.md)

### 1. Local app

```bash
cd app
docker build -t app:local .
docker run -p 8080:8080 app:local
curl http://localhost:8080/health
pytest -q
```

### 2. Full pipeline on Jenkins

Push to `main` (or run job manually). Confirm all stages complete through **Pipeline validation**.

Optional failure alert: set job env `SLACK_WEBHOOK_URL` — [monitoring.md](docs/monitoring.md).

### 3. Infrastructure

```bash
cd terraform && terraform init && terraform validate
aws eks describe-cluster --name devops-capstone --region ap-south-1 --query cluster.status
kubectl get nodes
```

Teardown when not in use: `terraform destroy` — [cost-optimization.md](docs/cost-optimization.md).

### 4. Application on EKS

```bash
kubectl get deploy,svc,hpa -n capstone-app
APP=$(kubectl get svc capstone-app -n capstone-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -sf "http://${APP}/health"
curl -sf "http://${APP}/metrics" | head
```

Rollback: [pipeline.md](docs/pipeline.md).

### 5. Monitoring

```bash
kubectl get pods -n monitoring
kubectl get svc grafana -n monitoring
```

Grafana (dev): `admin` / `capstone-dev` — dashboard **Capstone — App & Cluster**.  
Prometheus targets should include app pods, kube-state-metrics, and node-exporter.

Full checklist: [e2e-testing.md](docs/e2e-testing.md).

### 6. Demo / viva

[docs/demo-script.md](docs/demo-script.md) — 5–10 minute walkthrough of all five capstone stages.

---

## Documentation index

| Topic | File |
|-------|------|
| Capstone requirements | [docs/task.md](docs/task.md) |
| Architecture & IAM | [docs/architecture.md](docs/architecture.md) |
| Jenkins & ECR setup | [docs/sprint-1.md](docs/sprint-1.md) |
| Terraform & EKS | [docs/terraform.md](docs/terraform.md) |
| Ansible | [docs/ansible.md](docs/ansible.md) |
| Deploy pipeline | [docs/pipeline.md](docs/pipeline.md) |
| Kubernetes manifests | [docs/kubernetes.md](docs/kubernetes.md) |
| Monitoring & alerts | [docs/monitoring.md](docs/monitoring.md) |
| Jenkins triggers | [docs/jenkins-triggers.md](docs/jenkins-triggers.md) |
| End-to-end testing | [docs/e2e-testing.md](docs/e2e-testing.md) |
| Cost optimization (10%) | [docs/cost-optimization.md](docs/cost-optimization.md) |
| Production readiness | [docs/sprint-6.md](docs/sprint-6.md) |
| Screenshot list | [docs/screenshots/README.md](docs/screenshots/README.md) |

---

## Deliverables (Project 4)

- End-to-end Jenkins pipeline — build, Terraform, Ansible, deploy, test, monitoring
- AWS infrastructure via Terraform — VPC, EKS, S3 state (Jenkins EC2 bootstrap documented in [terraform.md](docs/terraform.md))
- Ansible configuration management in pipeline
- Application on EKS with health checks and HPA
- Prometheus, Grafana, and Prometheus alert rules
- Documentation, cost guide, and demo script

---

## Cost notes

Single NAT, `t3.medium` nodes, destroy EKS between study sessions. Details: [docs/cost-optimization.md](docs/cost-optimization.md).

---

## Lessons learned

- **IAM instance profiles** — Jenkins uses EC2 role, not committed access keys
- **SSM port-forward** — access Jenkins when corporate network blocks SSH/8080 ([sprint-1.md](docs/sprint-1.md))
- **EKS IAM** — caller permissions differ from cluster service roles ([terraform.md](docs/terraform.md))
- **metrics-server** — required on EKS for meaningful HPA CPU metrics ([pipeline.md](docs/pipeline.md))

More detail in each sprint log under `docs/`.
