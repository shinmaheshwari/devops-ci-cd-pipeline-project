# Sprint 6 — Testing, documentation, production readiness

## Status: complete in repo — verify with one full Jenkins run

## Deliverables added

| Artifact | Purpose |
|----------|---------|
| [e2e-testing.md](e2e-testing.md) | Manual + automated test checklist |
| [demo-script.md](demo-script.md) | 5–10 min viva walkthrough |
| [cost-optimization.md](cost-optimization.md) | Cost choices (10% evaluation) |
| [jenkins-triggers.md](jenkins-triggers.md) | SCM poll / webhook guidance |
| Jenkins **Pipeline validation** stage | Post-deploy cluster + metrics checks |
| Jenkins `triggers { pollSCM }` | Automated build on repo changes |

## Capstone pipeline stage mapping

| Capstone stage (task.md) | Jenkins stages |
|--------------------------|----------------|
| Build | Test, Build image, Push to ECR |
| Infrastructure | Terraform Init, Plan, Apply |
| Configuration | Ansible Configure |
| Deployment | Deploy, Post-deploy smoke test |
| Testing & monitoring | Pipeline validation, Monitoring |

## Definition of done

- [x] Automated tests in pipeline (pytest + smoke + validation stage)
- [x] E2E test documentation
- [x] Documentation index updated in README
- [x] SCM trigger documented + pollSCM in Jenkinsfile
- [x] Cost optimization document
- [x] Demo script
- [ ] Final unattended pipeline run captured (screenshots/logs — your Jenkins)

## Known limitations

- Jenkins EC2 not managed by Terraform (Sprint 1 bootstrap) — see [terraform.md](terraform.md#out-of-scope-in-terraform-documented-for-taskmd).
- Grafana admin password is hard-coded for demo (`monitoring/grafana.yaml`).
- Slack alerts require `SLACK_WEBHOOK_URL` on the Jenkins job (documented in [monitoring.md](monitoring.md)).
- Submission PNGs: add under [screenshots/README.md](screenshots/README.md).
