# Viva / demo script (5–10 minutes)

Walk through the **five capstone pipeline stages** mapped to this repository’s single Jenkinsfile.

## 0. Setup (30 seconds)

- Repo: `devops-ci-cd-pipeline-project`, region `ap-south-1`
- Show architecture diagram in [architecture.md](architecture.md) or README

## 1. Build stage (1–2 min)

**Say:** Git push triggers Jenkins; we build a multi-stage Docker image and push to ECR.

**Show:**

- `app/Dockerfile` — non-root user, `/health`
- Jenkins stages: **Test**, **Build image**, **Push to ECR**
- ECR console or `aws ecr describe-images`

## 2. Infrastructure provisioning (1–2 min)

**Say:** Terraform provisions VPC, EKS, remote state in S3; same pipeline keeps infra in sync with code.

**Show:**

- `terraform/modules/vpc`, `terraform/modules/eks`
- Jenkins: **Terraform Init / Plan / Apply**
- `docs/terraform.md` — cost and destroy notes

## 3. Configuration management (1 min)

**Say:** Ansible configures the Jenkins host after infra exists — Docker, kubectl, kubeconfig.

**Show:**

- `ansible/site.yml`, roles `common` + `jenkins`
- Jenkins: **Ansible Configure**

## 4. Deployment (2 min)

**Say:** We apply Kubernetes manifests, set the image tag from this build, and smoke-test the public LoadBalancer.

**Show:**

- `kubernetes/deployment.yaml` — probes, HPA
- Jenkins: **Deploy**, **Post-deploy smoke test**
- `curl` `/health` on app URL

## 5. Testing and monitoring (1–2 min)

**Say:** Unit tests run in CI; post-deploy we validate the cluster and scrape app metrics with Prometheus/Grafana.

**Show:**

- `app/tests/test_app.py`
- Jenkins: **Pipeline validation**, **Monitoring**
- Grafana or Prometheus targets (screenshot)

## Closing (30 seconds)

- Cost levers: [cost-optimization.md](cost-optimization.md)
- Full E2E checklist: [e2e-testing.md](e2e-testing.md)
- Known tradeoffs: single NAT, broad Jenkins IAM, dev Grafana password

## Q&A prep

- **Terraform vs Ansible?** Terraform creates AWS/EKS; Ansible configures the CI server.
- **Why metrics-server?** Default EKS lacks it; HPA needs real CPU metrics.
- **How does Jenkins access EKS?** Instance role + EKS access entries + kubeconfig for `jenkins` user.
