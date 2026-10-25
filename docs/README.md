# Documentation map

Use this page to navigate the repo for **submission**, **live demo**, and **deep dives**.

## Live demo (start here)

| Order | Doc | Use during demo |
|-------|-----|-----------------|
| 1 | **[live-demo-guide.md](live-demo-guide.md)** | 5–10 min script: what to say, what to open, Jenkins stage order |
| 2 | [architecture.md](architecture.md) | Mermaid diagram (GitHub → Jenkins → EKS) |
| 3 | [jenkins.md](jenkins.md) | How Jenkins is reached (SSM), job config, common failures |
| 4 | [screenshots/README.md](screenshots/README.md) | Evidence filenames if projector fails |

**Pipeline source of truth:** [jenkins/Jenkinsfile](../jenkins/Jenkinsfile) and [sprint-7.md](sprint-7.md).

## Runbooks (by topic)

| Topic | File | Not a rename of… |
|-------|------|------------------|
| Official requirements | [task.md](task.md) | — |
| Architecture & IAM | [architecture.md](architecture.md) | — |
| Jenkins server | [jenkins.md](jenkins.md) | Replaces re-reading all of [sprint-1.md](sprint-1.md) for setup |
| Terraform / EKS | [terraform.md](terraform.md) | Sprint 2 log + ops |
| Ansible | [ansible.md](ansible.md) | Sprint 3 |
| Deploy & rollback | [pipeline.md](pipeline.md) | Sprint 4 deploy detail (full pipeline order in sprint-7) |
| Kubernetes manifests | [kubernetes.md](kubernetes.md) | — |
| Monitoring & Slack | [monitoring.md](monitoring.md) | Sprint 5 |
| SCM triggers | [jenkins-triggers.md](jenkins-triggers.md) | — |
| E2E checklist | [e2e-testing.md](e2e-testing.md) | After demo or for grading evidence |
| Cost (10% eval) | [cost-optimization.md](cost-optimization.md) | — |

## Sprint logs (history & viva depth)

| Sprint | File | Content |
|--------|------|---------|
| 1 | [sprint-1.md](sprint-1.md) | Bootstrap, ECR, first Jenkins lessons |
| 2 | *(see [terraform.md](terraform.md))* | Infra runbook |
| 3 | *(see [ansible.md](ansible.md))* | Config runbook |
| 4 | *(see [pipeline.md](pipeline.md))* | Deploy runbook |
| 5 | *(see [monitoring.md](monitoring.md))* | Observability runbook |
| 6 | [sprint-6.md](sprint-6.md) | Sign-off, feedback table |
| 7 | [sprint-7.md](sprint-7.md) | Trivy, fail-fast, conditional Terraform |

## File naming (why we did not rename everything)

- **`sprint-N.md`** — historical logs tied to course sprints; renaming would break links and git history.
- **`live-demo-guide.md`** — single presenter script (clear name for viva).
- **`pipeline.md`** — deploy-focused runbook from Sprint 4; full stage list lives in **sprint-7** and **live-demo-guide**.
- **`plan.md`** — early roadmap only; **outdated** after implementation — do not use for demo.

## Screenshots

All under `docs/screenshots/` with prefix `sprintN-` matching README gallery sections.
