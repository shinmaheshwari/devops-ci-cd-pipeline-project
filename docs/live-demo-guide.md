# Live demo guide (5–10 minutes)

Presenter script aligned with **current** Jenkins order (Sprint 7). Evaluators think in five capstone stages from [task.md](task.md); the UI shows more granular stage names — use both.

## Before you start

- [ ] Jenkins job `capstone-build`, branch `*/main`, script `jenkins/Jenkinsfile`
- [ ] EKS cluster up (or trigger a build and wait through Terraform)
- [ ] SSM port-forward to Jenkins UI if needed — [jenkins.md](jenkins.md)
- [ ] Tabs ready: GitHub repo, Jenkins Stage View, AWS Console (EKS/ECR optional)
- [ ] Screenshot fallback: [screenshots/sprint7-pipeline-stage-order.png](screenshots/sprint7-pipeline-stage-order.png)

---

## Actual Jenkins stage order (what the UI shows)

```
Checkout → Test → Build image → Scan image → Push to ECR
  → Terraform Init → Terraform Plan → Terraform Apply (if changes)
  → Ansible Configure → Deploy → Post-deploy smoke test
  → Monitoring → Pipeline validation
```

Detail: [sprint-7.md](sprint-7.md).

---

## Capstone stage 1 — Build (≈2 min)

**Say:** Code push triggers Jenkins. We run tests first, build a multi-stage image, scan with Trivy for CRITICAL CVEs, then push to ECR. Fail-fast: nothing touches AWS if tests or scan fail.

**Show:**

| Item | Where |
|------|--------|
| Dockerfile, `/health` | `app/Dockerfile`, `app/app.py` |
| Unit tests | `app/tests/test_app.py` — Jenkins **Test** |
| Trivy gate | Jenkins **Scan image** — [sprint7-trivy-scan-passed.png](screenshots/sprint7-trivy-scan-passed.png) |
| ECR | **Push to ECR** or AWS Console |

**Capstone mapping:** Build + test + registry.

---

## Capstone stage 2 — Infrastructure (≈2 min)

**Say:** Terraform provisions VPC, subnets, NAT, EKS, and stores state in S3. Apply runs only when the plan detects changes (app-only commits skip apply).

**Show:**

| Item | Where |
|------|--------|
| Modules | `terraform/modules/vpc`, `terraform/modules/eks` |
| Jenkins | **Terraform Init / Plan / Apply** |
| Skip apply | [sprint7-terraform-apply-skipped.png](screenshots/sprint7-terraform-apply-skipped.png) |
| Ops | [terraform.md](terraform.md) — destroy/cost |

**Capstone mapping:** Infrastructure provisioning + remote state.

---

## Capstone stage 3 — Configuration (≈1 min)

**Say:** Ansible configures the Jenkins host after infra exists: Docker, kubectl, kubeconfig, validation.

**Show:**

| Item | Where |
|------|--------|
| Playbook | `ansible/site.yml`, roles `common`, `jenkins` |
| Jenkins | **Ansible Configure** |
| Evidence | [sprint3-ansible-console.png](screenshots/sprint3-ansible-console.png) |

**Capstone mapping:** Configuration management on EC2 (CI host).

---

## Capstone stage 4 — Deployment (≈2 min)

**Say:** We deploy to EKS with manifests, pin the image tag from this build, install metrics-server for HPA, and smoke-test the public load balancer.

**Show:**

| Item | Where |
|------|--------|
| Manifests | `kubernetes/` — [kubernetes.md](kubernetes.md) |
| Jenkins | **Deploy**, **Post-deploy smoke test** |
| Live app | [sprint7-app-health.png](screenshots/sprint7-app-health.png) or `curl` LB `/health` |
| HPA | [sprint4-hpa-metrics.png](screenshots/sprint4-hpa-metrics.png) |

**Capstone mapping:** Kubernetes deploy, LB, health checks, autoscaling.

---

## Capstone stage 5 — Test & monitor (≈2 min)

**Say:** Post-deploy we apply monitoring, validate metrics endpoints, and use Prometheus/Grafana for app and node metrics. Pipeline failures can notify Slack.

**Show:**

| Item | Where |
|------|--------|
| Monitoring stack | `monitoring/` — [monitoring.md](monitoring.md) |
| Jenkins | **Monitoring**, **Pipeline validation** |
| Prometheus targets | [sprint5-prometheus-targets.png](screenshots/sprint5-prometheus-targets.png) |
| Grafana dashboard | Port-forward + [sprint5-grafana-dashboard.png](screenshots/sprint5-grafana-dashboard.png) |
| Slack (optional) | [sprint5-slack-alert.png](screenshots/sprint5-slack-alert.png) |

**Capstone mapping:** Testing + observability + alerts.

---

## Closing (30 s)

- Cost: [cost-optimization.md](cost-optimization.md)
- Full checklist: [e2e-testing.md](e2e-testing.md)
- Architecture: [architecture.md](architecture.md)

---

## Q&A quick answers

| Question | Answer |
|----------|--------|
| Terraform vs Ansible? | Terraform creates AWS/EKS; Ansible configures the Jenkins CI server. |
| Why CI before Terraform? | Fail fast; avoid 10+ min apply on broken code ([sprint-7.md](sprint-7.md)). |
| Why Trivy? | Block CRITICAL vulnerabilities before ECR/EKS. |
| Why metrics-server? | EKS does not include it; HPA needs it for CPU %. |
| Jenkins → EKS auth? | EC2 instance profile; cluster creator access when Jenkins runs Terraform ([terraform.md](terraform.md)). |
| Why Grafana port-forward? | ClusterIP by design — dev password in repo ([monitoring.md](monitoring.md)). |
