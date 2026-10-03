# End-to-end testing

Use this checklist after a full Jenkins pipeline run (or a manual replay of each stage) to confirm the capstone path from **git push → running app → monitoring**.

## Preconditions

- Jenkins job `capstone-build` uses **Pipeline script from SCM**, branch `*/main` (or your feature branch for stacked PR testing).
- AWS credentials via Jenkins EC2 **instance profile** (no keys in git).
- EKS cluster exists (`terraform apply` succeeded in pipeline).

## Automated coverage in Jenkins

| Stage | What is validated |
|-------|-------------------|
| Test | `pytest` unit tests (`app/tests/`) |
| Post-deploy smoke test | Public LoadBalancer `/health` returns 200 |
| Pipeline validation | Deployments, HPA, monitoring pods, in-cluster `/metrics` |

## Manual verification (recommended for submission evidence)

### 1. Infrastructure

```bash
aws eks describe-cluster --name devops-capstone --region ap-south-1 --query cluster.status
kubectl get nodes
```

### 2. Application

```bash
kubectl get deploy,svc,hpa -n capstone-app
APP_HOST=$(kubectl get svc capstone-app -n capstone-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -sf "http://${APP_HOST}/health"
curl -sf "http://${APP_HOST}/metrics" | head
```

### 3. Monitoring

```bash
kubectl get pods -n monitoring
kubectl port-forward svc/prometheus -n monitoring 9090:9090
# Browser: http://localhost:9090/targets — capstone-app pods UP
```

### 4. Autoscaling signal

```bash
kubectl get hpa -n capstone-app
# CPU should show a percentage (not <unknown>) after metrics-server is installed
```

### 5. Rollback drill (optional)

```bash
kubectl rollout undo deployment/capstone-app -n capstone-app
kubectl rollout status deployment/capstone-app -n capstone-app
```

## Failure scenarios to rehearse

| Symptom | Likely cause | Doc reference |
|---------|--------------|---------------|
| HPA CPU `<unknown>` | metrics-server missing | [pipeline.md](pipeline.md) |
| Jenkins “success” but old pipeline | Wrong branch specifier | [pipeline.md](pipeline.md) |
| `kubectl` unauthorized after recreate | EKS access / bootstrap | [terraform.md](terraform.md), EKS `access_config` |
| Docker permission denied | jenkins not in docker group | [ansible.md](ansible.md) |

## Definition of done (Sprint 6)

- [ ] One unattended pipeline run from SCM trigger completes all stages
- [ ] Manual checklist above passes with screenshots or console logs archived
- [ ] [demo-script.md](demo-script.md) rehearsed once end-to-end
