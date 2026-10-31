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

## Sprint 7
- `sprint7-pipeline-stage-order.png` — full run with the new stage order
- `sprint7-trivy-scan-failed.png` — scan gate blocking 3 CRITICAL vulnerabilities
- `sprint7-trivy-scan-passed.png` — rescan after `--pull`: `Total: 0`
- `sprint7-terraform-apply-skipped.png` — no infrastructure changes, Terraform Apply skipped
- `sprint7-fail-fast.png` — failing test stops the pipeline before Terraform
- `sprint7-slack-fail-fast.png` — Slack alerts for failed builds
- `sprint7-terraform-import.png` — Jenkins access entry imported into state
- `sprint7-app-health.png` — `/health` through the load balancer
- `sprint7-metrics-server-pinned.png` — metrics-server on the pinned `v0.7.2` image
- `sprint7-hpa-before.png` — `kubectl get hpa,deploy`: 2 replicas, CPU 1% of target
- `sprint7-hpa-scaling-up.png` — `kubectl get hpa -w` while CPU rises and replicas increase
- `sprint7-hpa-pods-scaled.png` — `kubectl get pods -o wide` and `kubectl top pods` with 5 replicas
- `sprint7-grafana-load-test.png` — Grafana dashboard during the load test
- `sprint7-hpa-scaled-down.png` — back to 2 replicas after the load stopped

Do not commit secrets in screenshots (webhook URLs, tokens). Crop them out first.

## Cost
- `cost-explorer-actual.png` — `aws ce get-cost-and-usage` output: usage before credits, by service, and credits applied
