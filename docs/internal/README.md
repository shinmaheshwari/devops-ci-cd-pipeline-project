# Internal documentation (team only)

Not linked from the root **README** — for install, demo prep, and interview practice.

| Doc | Purpose |
|-----|---------|
| [dev-setup-guide.md](dev-setup-guide.md) | Full bootstrap: AWS, Jenkins EC2, ECR, Terraform backend, Jenkins job |
| [project-walkthrough.md](project-walkthrough.md) | End-to-end mental model: repos, pipeline, data flow |
| [live-demo-guide.md](live-demo-guide.md) | 5–10 min presenter script |
| [interview-qa.md](interview-qa.md) | Common viva / interview questions and answers |

Public submission docs live under `docs/` and are indexed from the repository [README.md](../../README.md).

**Repo hygiene:** Close stale stacked PRs **#4, #7, #8** if `main` already contains Sprints 5–7 (merged via #9 and later PRs).

## Submission vs internal (after PR #11)

| Area | Public (`README.md`, `docs/*.md`) | Internal only (`docs/internal/`) |
|------|-----------------------------------|----------------------------------|
| Install / bootstrap | Pointers in Quickstart + runbooks | [dev-setup-guide.md](dev-setup-guide.md) full sequence |
| Live demo / viva script | Not in root README | [live-demo-guide.md](live-demo-guide.md) |
| Interview prep | — | [interview-qa.md](interview-qa.md) |
| Whole-project narrative | [architecture.md](../architecture.md), sprint logs | [project-walkthrough.md](project-walkthrough.md) |

## Gaps already documented (not blockers for demo)

| Topic | Status |
|-------|--------|
| Jenkins EC2 + SG | Manual bootstrap — [terraform.md](../terraform.md#out-of-scope-in-terraform-documented-for-taskmd) |
| ECR / S3 backend | One-time AWS console/CLI — [dev-setup-guide.md](dev-setup-guide.md) |
| Git webhook vs pollSCM | pollSCM in Jenkinsfile — [jenkins-triggers.md](../jenkins-triggers.md) |
| Grafana admin password in manifests | Dev/demo only — mention in viva ([interview-qa.md](interview-qa.md)) |

## Before merge of PR #11

- [ ] Root README has **no** links to `docs/internal/` or live-demo
- [ ] `docs/live-demo-guide.md` and `docs/README.md` removed (hub = root README + this folder)
- [ ] Update PR #11 description to reflect internal/public split (old body still references public live-demo-guide)
- [ ] Rehearse once using [live-demo-guide.md](live-demo-guide.md) against Jenkins Stage View
