# Live demo guide (internal, 5–10 minutes)

Presenter script — Sprint 7 Jenkins order. Public requirements: [task.md](../task.md).

## Before you start

- [ ] Jenkins job `capstone-build`, branch `*/main`, script `jenkins/Jenkinsfile`
- [ ] EKS cluster up (or trigger build and wait through Terraform)
- [ ] SSM port-forward to Jenkins — [jenkins.md](../jenkins.md)
- [ ] Fallback: [../screenshots/sprint7-pipeline-stage-order.png](../screenshots/sprint7-pipeline-stage-order.png)

## Jenkins stage order (UI)

```
Checkout → Test → Build image → Scan image → Push to ECR
  → Terraform Init → Plan → Apply (if changes)
  → Ansible Configure → Deploy → Post-deploy smoke test
  → Monitoring → Pipeline validation
```

See [sprint-7.md](../sprint-7.md).

## Capstone stage 1 — Build

**Say:** Tests, multi-stage Docker build, Trivy, ECR push — fail-fast before AWS.

**Show:** `app/Dockerfile`, Jenkins Test/Scan/Push, [sprint7-trivy-scan-passed.png](../screenshots/sprint7-trivy-scan-passed.png).

## Capstone stage 2 — Infrastructure

**Say:** Terraform VPC/EKS, S3 state, conditional apply.

**Show:** `terraform/modules/*`, [sprint7-terraform-apply-skipped.png](../screenshots/sprint7-terraform-apply-skipped.png).

## Capstone stage 3 — Configuration

**Say:** Ansible on Jenkins host.

**Show:** `ansible/site.yml`, [sprint3-ansible-console.png](../screenshots/sprint3-ansible-console.png).

## Capstone stage 4 — Deployment

**Say:** kubectl, metrics-server, LB smoke test.

**Show:** `kubernetes/`, [sprint7-app-health.png](../screenshots/sprint7-app-health.png).

## Capstone stage 5 — Test & monitor

**Say:** Prometheus/Grafana, validation, optional Slack.

**Show:** [sprint5-prometheus-targets.png](../screenshots/sprint5-prometheus-targets.png), [sprint5-grafana-dashboard.png](../screenshots/sprint5-grafana-dashboard.png).

## Closing

[cost-optimization.md](../cost-optimization.md) · [e2e-testing.md](../e2e-testing.md) · [interview-qa.md](interview-qa.md)
