# Project walkthrough (internal)

Understand the whole system before demo or interviews.

## What problem this solves

Automate: **test → build → secure → publish image → provision AWS → configure CI host → deploy to Kubernetes → observe** — one Jenkins pipeline, one git repo.

## Components

| Layer | Technology | Directory |
|-------|------------|-----------|
| App | Flask + gunicorn | `app/` |
| CI/CD | Jenkins on EC2 | `jenkins/Jenkinsfile` |
| Registry | ECR | AWS (manual create) |
| IaC | Terraform | `terraform/` |
| Config | Ansible (localhost on Jenkins) | `ansible/` |
| Runtime | EKS + manifests | `kubernetes/` |
| Observability | Prometheus, Grafana, exporters | `monitoring/` |

## Pipeline flow (Sprint 7)

```
Git push → Jenkins
  → CI block: pytest, docker build (--pull), Trivy, ECR push
  → Infra block: terraform init/validate/plan/apply (if changes)
  → Ansible on Jenkins host
  → kubectl deploy app + metrics-server
  → smoke test (public LB)
  → monitoring stack + validation
```

Capstone **five stages** map to these blocks — see [live-demo-guide.md](live-demo-guide.md).

## What Terraform owns vs manual

| Resource | Owner |
|----------|--------|
| Jenkins EC2 | Manual ([terraform.md](../terraform.md)) |
| ECR repo | Manual |
| S3/DynamoDB backend | Manual bootstrap |
| VPC, NAT, EKS, node group | Terraform |

## What Ansible does (and does not)

- **Does:** Install/update Docker, kubectl, AWS CLI on **Jenkins EC2**; kubeconfig; validate `kubectl get nodes`.
- **Does not:** SSH to EKS worker nodes (AWS manages them).

## Security highlights

- No AWS access keys in git — instance profile.
- Trivy blocks CRITICAL CVEs before push.
- Grafana ClusterIP + port-forward (password in repo — dev only).
- Slack webhook in Jenkins credentials.

## Key failure modes (already hit once)

| Issue | Where documented |
|-------|------------------|
| Wrong Jenkins branch | [jenkins.md](../jenkins.md), [pipeline.md](../pipeline.md) |
| HPA CPU unknown | metrics-server in Deploy stage |
| EKS auth after recreate | [sprint-7.md](../sprint-7.md), [terraform.md](../terraform.md) |
| Stale Docker base / Trivy fail | `docker build --pull`, [sprint-7.md](../sprint-7.md) |
| Ansible apt / sudo | [jenkins.md](../jenkins.md), [sprint-6.md](../sprint-6.md) |

## Read order for deep understanding

1. [code-and-setup-walkthrough.md](code-and-setup-walkthrough.md) — phased setup with file-level explanation
2. [architecture.md](../architecture.md)
3. [pipeline.md](../pipeline.md) + [sprint-7.md](../sprint-7.md)
4. Skim `jenkins/Jenkinsfile`
5. [monitoring.md](../monitoring.md)
6. [sprint-6.md](../sprint-6.md) feedback table
