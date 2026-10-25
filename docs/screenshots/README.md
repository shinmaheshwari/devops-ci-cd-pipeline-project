# Submission screenshots

PNG captures referenced by [README.md](../../README.md). Keep these exact filenames so the images render on GitHub.

## Sprint 1
- `sprint1-jenkins-dashboard.png`
- `sprint1-jenkins-console.png`
- `sprint1-ecr-repo.png`
- `sprint1-ec2-instance.png`

## Sprint 2
- `sprint2-kubectl-nodes.png`
- `sprint2-eks-cluster.png`
- `sprint2-vpc.png`
- `sprint2-terraform-apply.png`
- `sprint2-jenkins-terraform-pipeline.png`

## Sprint 3
- `sprint3-ansible-console.png` — Jenkins console, `PLAY RECAP` with `failed=0`
- `sprint3-jenkins-host-tools.png` — docker / kubectl / aws versions and `kubectl get nodes` on the Jenkins host
- `sprint3-pr-merged.png` — PR #2 with the Merged badge

## Sprint 4
- `sprint4-pods-running.png` — `kubectl get pods -n capstone-app`
- `sprint4-hpa-metrics.png` — `kubectl get hpa -n capstone-app` with a real CPU percentage
- `sprint4-app-live.png` — `/health` through the load balancer URL
- `sprint4-jenkins-deploy.png` — Deploy and smoke test stages succeeding

## Sprint 5
- `sprint5-prometheus-targets.png` — app, kube-state-metrics and node-exporter targets UP
- `sprint5-grafana-dashboard.png` — **Capstone — App & Cluster** dashboard
- `sprint5-alert-firing.png` — `CapstoneAppDown` firing during the failure test
- `sprint5-jenkins-monitoring.png` — Jenkins Monitoring stage succeeding
- `sprint5-slack-alert.png` — Slack channel showing the failure notification

## Sprint 6
- `sprint6-final-pipeline.png` — one complete green pipeline run (Stage View)

## Sprint 7 (live demo)
- `sprint7-pipeline-stage-order.png` — Stage View with CI-before-Terraform order
- `sprint7-trivy-scan-passed.png` / `sprint7-trivy-scan-failed.png` — security gate
- `sprint7-terraform-apply-skipped.png` — conditional apply
- `sprint7-fail-fast.png` / `sprint7-slack-fail-fast.png` — test fails before Terraform
- `sprint7-app-health.png` — `/health` via load balancer
- `sprint7-metrics-server-pinned.png` — pinned metrics-server image
- `sprint7-terraform-import.png` — import recovery (optional Q&A)

Do not commit secrets in screenshots (webhook URLs, tokens). Crop them out first.
