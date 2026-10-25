# Project 4 — End-to-End DevOps CI/CD Capstone

Automated pipeline for a Dockerized Flask app on **AWS EKS**, orchestrated by **Jenkins**: CI and image scanning, infrastructure (Terraform), configuration (Ansible), deployment (Kubernetes), and observability (Prometheus/Grafana).

| Evaluation (per [docs/task.md](docs/task.md)) | Weight |
|-----------------------------------------------|--------|
| Implementation | 75% |
| Documentation | 15% |
| Cost optimization | 10% |

**Region:** `ap-south-1` · **Requirements:** [docs/task.md](docs/task.md)

**Live demo:** start with **[docs/live-demo-guide.md](docs/live-demo-guide.md)** · **All docs:** [docs/README.md](docs/README.md)

---

## Architecture

High-level diagram and IAM boundaries: **[docs/architecture.md](docs/architecture.md)** (Mermaid: GitHub → Jenkins → ECR / Terraform / EKS / monitoring).

---

## Project goals (task mapping)

| Goal | Delivery | Documentation |
|------|----------|---------------|
| Architecture (LB, orchestration, monitoring) | VPC, EKS, LoadBalancer Service, Prometheus/Grafana | [architecture.md](docs/architecture.md) |
| Terraform (VPC, subnets, EKS, S3 state) | `terraform/` + Jenkins Terraform stages | [terraform.md](docs/terraform.md) |
| Ansible configuration | `ansible/` after Terraform | [ansible.md](docs/ansible.md) |
| App on EKS (scale, resilience) | `kubernetes/` — probes, HPA | [kubernetes.md](docs/kubernetes.md) |
| Jenkins CI/CD | [jenkins/Jenkinsfile](jenkins/Jenkinsfile) | [pipeline.md](docs/pipeline.md), [jenkins.md](docs/jenkins.md) |
| Prometheus & Grafana | `monitoring/` — app + node metrics | [monitoring.md](docs/monitoring.md) |

---

## Jenkins pipeline (current)

Declarative pipeline: [jenkins/Jenkinsfile](jenkins/Jenkinsfile). **Sprint 7** runs CI and image scan **before** Terraform so tests fail fast and vulnerable images never reach ECR. Details: [sprint-7.md](docs/sprint-7.md).

| Capstone stage ([task.md](docs/task.md)) | Jenkins stages |
|------------------------------------------|----------------|
| **1. Build** | Test → Build image → **Scan image (Trivy)** → Push to ECR |
| **2. Infrastructure** | Terraform Init → Plan → Apply *(only if plan has changes)* |
| **3. Configuration** | Ansible Configure |
| **4. Deployment** | Deploy → Post-deploy smoke test |
| **5. Test & monitor** | Monitoring → Pipeline validation |

**Trigger:** Git push or SCM poll (~15 min) — [jenkins-triggers.md](docs/jenkins-triggers.md).

```
Checkout → Test → Build → Scan → Push ECR → Terraform → Ansible → Deploy → Smoke → Monitoring → Validation
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
docs/          # Runbooks, sprint logs, screenshots
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
| 7 | Fail-fast CI, Trivy, conditional Terraform apply | [sprint-7.md](docs/sprint-7.md) |

---

## Evidence screenshots

### Sprint 1 — Docker, ECR, Jenkins

![Jenkins dashboard](docs/screenshots/sprint1-jenkins-dashboard.png)
![Jenkins console output](docs/screenshots/sprint1-jenkins-console.png)
![ECR repository](docs/screenshots/sprint1-ecr-repo.png)
![Jenkins EC2 instance](docs/screenshots/sprint1-ec2-instance.png)

### Sprint 2 — Terraform (VPC + EKS)

![kubectl get nodes](docs/screenshots/sprint2-kubectl-nodes.png)
![EKS cluster](docs/screenshots/sprint2-eks-cluster.png)
![VPC](docs/screenshots/sprint2-vpc.png)
![terraform apply](docs/screenshots/sprint2-terraform-apply.png)
![Jenkins pipeline with Terraform stages](docs/screenshots/sprint2-jenkins-terraform-pipeline.png)

### Sprint 3 — Ansible

![Ansible play recap in Jenkins](docs/screenshots/sprint3-ansible-console.png)
![Tooling on the Jenkins host](docs/screenshots/sprint3-jenkins-host-tools.png)

### Sprint 4 — Deploy to EKS

![Pods running](docs/screenshots/sprint4-pods-running.png)
![HPA with live CPU metrics](docs/screenshots/sprint4-hpa-metrics.png)
![App reachable through the load balancer](docs/screenshots/sprint4-app-live.png)
![Jenkins Deploy and smoke test](docs/screenshots/sprint4-jenkins-deploy.png)

### Sprint 5 — Monitoring and alerting

![Prometheus targets](docs/screenshots/sprint5-prometheus-targets.png)
![Grafana dashboard](docs/screenshots/sprint5-grafana-dashboard.png)
![CapstoneAppDown alert firing](docs/screenshots/sprint5-alert-firing.png)
![Jenkins Monitoring stage](docs/screenshots/sprint5-jenkins-monitoring.png)
![Slack failure notification](docs/screenshots/sprint5-slack-alert.png)

### Sprint 6 — Full pipeline

![Complete pipeline run](docs/screenshots/sprint6-final-pipeline.png)

### Sprint 7 — Post-review hardening

![Pipeline stage order](docs/screenshots/sprint7-pipeline-stage-order.png)
![Trivy scan passed](docs/screenshots/sprint7-trivy-scan-passed.png)
![Terraform apply skipped when no changes](docs/screenshots/sprint7-terraform-apply-skipped.png)
![Fail-fast before Terraform](docs/screenshots/sprint7-fail-fast.png)
![App health via load balancer](docs/screenshots/sprint7-app-health.png)

More filenames: [docs/screenshots/README.md](docs/screenshots/README.md).

---

## Step-by-step — run the project

### Prerequisites

- AWS account (EKS, ECR, VPC, S3, DynamoDB)
- Jenkins on EC2 — build and access: **[docs/jenkins.md](docs/jenkins.md)**
- Job: **Pipeline from SCM**, script path `jenkins/Jenkinsfile`, branch `*/main`
- ECR repo `devops-capstone-app` and Terraform S3 backend — [terraform.md](docs/terraform.md)
- Jenkins credential `slack-webhook-url` (optional, for failure alerts) — [monitoring.md](docs/monitoring.md)

### 1. Local app

```bash
cd app
docker build -t app:local .
docker run -p 8080:8080 app:local
curl http://localhost:8080/health
pytest -q
```

### 2. Full pipeline on Jenkins

Push to `main` or run the job manually. Confirm all stages through **Pipeline validation** (see [e2e-testing.md](docs/e2e-testing.md)).

### 3. Infrastructure

```bash
cd terraform && terraform init && terraform validate
aws eks describe-cluster --name devops-capstone --region ap-south-1 --query cluster.status
kubectl get nodes
```

Teardown when idle: `terraform destroy` — [cost-optimization.md](docs/cost-optimization.md).

### 4. Application on EKS

```bash
kubectl get deploy,svc,hpa -n capstone-app
APP=$(kubectl get svc capstone-app -n capstone-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -sf "http://${APP}/health"
curl -sf "http://${APP}/metrics" | head
```

Rollback: [pipeline.md](docs/pipeline.md) · Manifests: [kubernetes.md](docs/kubernetes.md).

### 5. Monitoring

```bash
kubectl get pods -n monitoring
kubectl port-forward svc/grafana -n monitoring 3000:80
kubectl port-forward svc/prometheus -n monitoring 9090:9090
```

Grafana (dev): `admin` / `capstone-dev` — dashboard **Capstone — App & Cluster**.

### 6. Demo / viva

**[docs/live-demo-guide.md](docs/live-demo-guide.md)** — 5–10 min script (capstone stages + actual Jenkins UI order).

---

## Documentation index

| Topic | File |
|-------|------|
| **Live demo script** | **[docs/live-demo-guide.md](docs/live-demo-guide.md)** |
| Doc map & naming | [docs/README.md](docs/README.md) |
| Capstone requirements | [docs/task.md](docs/task.md) |
| Architecture & IAM | [docs/architecture.md](docs/architecture.md) |
| Jenkins server setup & troubleshooting | [docs/jenkins.md](docs/jenkins.md) |
| Sprint 1 log | [docs/sprint-1.md](docs/sprint-1.md) |
| Terraform & EKS | [docs/terraform.md](docs/terraform.md) |
| Ansible | [docs/ansible.md](docs/ansible.md) |
| Deploy pipeline | [docs/pipeline.md](docs/pipeline.md) |
| Kubernetes manifests | [docs/kubernetes.md](docs/kubernetes.md) |
| Monitoring & alerts | [docs/monitoring.md](docs/monitoring.md) |
| Jenkins triggers | [docs/jenkins-triggers.md](docs/jenkins-triggers.md) |
| End-to-end testing | [docs/e2e-testing.md](docs/e2e-testing.md) |
| Cost optimization (10%) | [docs/cost-optimization.md](docs/cost-optimization.md) |
| Sprint 6 sign-off | [docs/sprint-6.md](docs/sprint-6.md) |
| Sprint 7 improvements | [docs/sprint-7.md](docs/sprint-7.md) |
| Screenshot checklist | [docs/screenshots/README.md](docs/screenshots/README.md) |

---

## Deliverables (Project 4)

- End-to-end Jenkins pipeline — build/scan, Terraform, Ansible, deploy, test, monitoring
- AWS infrastructure via Terraform — VPC, EKS, S3 state (Jenkins EC2 documented in [jenkins.md](docs/jenkins.md) / [terraform.md](docs/terraform.md))
- Ansible configuration management in pipeline
- Application on EKS with health checks and HPA
- Prometheus, Grafana, and alert rules (Slack on pipeline failure)
- Documentation, cost guide, demo script, and evidence screenshots

---

## Cost notes

Single NAT, `t3.medium` nodes, destroy EKS between study sessions. **[docs/cost-optimization.md](docs/cost-optimization.md)**

---

## Lessons learned (summary)

- **IAM instance profiles** — no AWS keys in git ([sprint-1.md](docs/sprint-1.md))
- **SSM port-forward** — Jenkins access behind corporate proxy ([jenkins.md](docs/jenkins.md))
- **EKS IAM** — caller vs cluster service roles ([terraform.md](docs/terraform.md))
- **metrics-server** — required for HPA CPU metrics ([pipeline.md](docs/pipeline.md))
- **Fail-fast + Trivy** — CI before Terraform; block CRITICAL CVEs ([sprint-7.md](docs/sprint-7.md))

Full troubleshooting in sprint logs under `docs/`.
