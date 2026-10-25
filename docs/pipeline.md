# Jenkins pipeline — deploy and operations

Deploy-stage detail from Sprint 4, plus the **current full pipeline order** (Sprint 7).

## Full pipeline order (source of truth)

See [sprint-7.md](sprint-7.md) and [jenkins/Jenkinsfile](../jenkins/Jenkinsfile).

```
Checkout → Test → Build image → Scan image → Push to ECR
  → Terraform Init → Plan → Apply (only if plan has changes)
  → Ansible Configure → Deploy → Post-deploy smoke test
  → Monitoring → Pipeline validation
```

## Capstone stage mapping

| Capstone stage ([task.md](task.md)) | Jenkins stages |
|-------------------------------------|----------------|
| Build | Test, Build image, Scan image, Push to ECR |
| Infrastructure | Terraform Init, Plan, Apply |
| Configuration | Ansible Configure |
| Deployment | Deploy, Post-deploy smoke test |
| Test & monitor | Monitoring, Pipeline validation |

## What the Deploy stage does

1. `aws eks update-kubeconfig` — points kubectl at the current cluster
2. Applies **metrics-server** (pinned `v0.7.2`) — required for HPA CPU metrics on EKS
3. Applies `kubernetes/*.yaml` (namespace, deployment, service, hpa)
4. `kubectl set image` — image tag from **this** build (`BUILD_NUMBER`-`git sha`)
5. `kubectl rollout status` — waits for rollout
6. **Post-deploy smoke test** — polls LoadBalancer hostname, curls `/health`

## Rollback

```bash
kubectl rollout undo deployment/capstone-app -n capstone-app
kubectl rollout status deployment/capstone-app -n capstone-app
```

## Verify deployment

```bash
kubectl get pods -n capstone-app
kubectl get hpa -n capstone-app         # CPU % not <unknown>
kubectl get svc capstone-app -n capstone-app
curl -sf "http://<lb-hostname>/health"
```

Manifest reference: [kubernetes.md](kubernetes.md).

## Lessons learned

1. **Metrics Server** — not default on EKS; HPA shows `<unknown>` without it.
2. **Branch Specifier** — must be `*/main` or builds look green but run stale code ([jenkins.md](jenkins.md)).
3. **EKS access after recreate** — cluster creator permissions; see [terraform.md](terraform.md) and [sprint-7.md](sprint-7.md).
4. **Smoke test on new LB** — allow DNS/propagation time (retry loop in Jenkinsfile).

Further monitoring and alerts: [monitoring.md](monitoring.md).
