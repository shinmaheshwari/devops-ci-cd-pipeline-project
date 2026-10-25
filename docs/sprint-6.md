# Sprint 6 — Testing, documentation, production readiness

## Status: complete — verified with a full Jenkins run (build #23, all stages green)

## Deliverables added

| Artifact | Purpose |
|----------|---------|
| [e2e-testing.md](e2e-testing.md) | Manual + automated test checklist |
| [live-demo-guide.md](live-demo-guide.md) | 5–10 min live demo / viva |
| [cost-optimization.md](cost-optimization.md) | Cost choices (10% evaluation) |
| [jenkins-triggers.md](jenkins-triggers.md) | SCM poll / webhook guidance |
| Jenkins **Pipeline validation** stage | Post-deploy cluster + metrics checks |
| Jenkins `triggers { pollSCM }` | Automated build on repo changes |

## Capstone pipeline stage mapping

Updated in Sprint 7 — full order: [sprint-7.md](sprint-7.md), [live-demo-guide.md](live-demo-guide.md).

| Capstone stage (task.md) | Jenkins stages |
|--------------------------|----------------|
| Build | Test, Build image, Scan image, Push to ECR |
| Infrastructure | Terraform Init, Plan, Apply (conditional) |
| Configuration | Ansible Configure |
| Deployment | Deploy, Post-deploy smoke test |
| Testing & monitoring | Monitoring, Pipeline validation |

## Definition of done

- [x] Automated tests in pipeline (pytest + smoke + validation stage)
- [x] E2E test documentation
- [x] Documentation index updated in README
- [x] SCM trigger documented + pollSCM in Jenkinsfile
- [x] Cost optimization document
- [x] Demo script
- [x] Final full pipeline run captured (build #23, `screenshots/sprint6-final-pipeline.png`)

## Known limitations

- Jenkins EC2 not managed by Terraform (Sprint 1 bootstrap) — see [terraform.md](terraform.md#out-of-scope-in-terraform-documented-for-taskmd).
- Grafana admin password is hard-coded for demo (`monitoring/grafana.yaml`); Grafana is `ClusterIP`, reachable only through `kubectl port-forward`.
- Slack alerts need the Jenkins credential `slack-webhook-url` (Secret text); without it the step is skipped (documented in [monitoring.md](monitoring.md)).
- `pollSCM` rebuilds on every new commit and the pipeline runs `terraform apply`, so **disable the Jenkins job while the cluster is destroyed** or a poll will recreate it.
- Submission PNGs are in `docs/screenshots/` (expected files listed in [screenshots/README.md](screenshots/README.md)).

## Feedback and adjustments

Review and real runs found issues that reading the code did not. Each was fixed before or during merge.

| Finding | Found by | Change |
|---|---|---|
| EKS access entries rejected: cluster had no `access_config` | Running PR #2 (Sprint 3) through Jenkins | `authentication_mode = "API_AND_CONFIG_MAP"` on the cluster |
| `jenkins` user had no sudo, so Ansible failed on the first task | Same run | Sudoers file for the `jenkins` user ([jenkins.md](jenkins.md)) |
| Ansible `apt` failed because of a stale HashiCorp apt source | Same run | Removed the source |
| `pipefail` failed under `/bin/sh` | Same run | `executable: /bin/bash` on the task |
| Cluster creator was locked out after every recreate | Two destroy and recreate cycles | `bootstrap_cluster_creator_admin_permissions = true` |
| Builds kept running an old branch and looked successful | Comparing image tags with commits | Branch specifier reset to `*/main`; check documented in [jenkins.md](jenkins.md) |
| Smoke test failed on a fresh load balancer (curl exit 6) | Two pipeline runs on new clusters | Retry loop in the smoke test |
| Grafana was a public load balancer with a hard-coded dev password | Review of the monitoring PR | `ClusterIP`, reached with `kubectl port-forward` |
| Slack step read an environment variable nothing set | Review of the monitoring PR | Reads the Jenkins credential `slack-webhook-url` |
| Documented alert test (scale to 0) cannot fire `CapstoneAppDown` | Running the test | Test changed to break scraping on one live pod |
| README rewrite dropped the screenshots | Diffing the PR stack against `main` | Gallery restored |
