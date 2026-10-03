# Kubernetes deployment

## Manifests (`kubernetes/`)

| File | Resource | Purpose |
|------|----------|---------|
| `namespace.yaml` | Namespace `capstone-app` | Isolates app resources |
| `deployment.yaml` | Deployment | 2 replicas, probes, resource limits, Prometheus scrape annotations |
| `service.yaml` | Service `LoadBalancer` | Public AWS ELB → port 80 → app 8080 |
| `hpa.yaml` | HorizontalPodAutoscaler | CPU 70%, min 2 / max 5 replicas |

Image tag in git is a placeholder (`:latest`). Jenkins **Deploy** runs `kubectl set image` with the tag built in that pipeline run.

## Health checks

- **Readiness** — `GET /health:8080` — pod receives traffic only when healthy
- **Liveness** — same path — restarts stuck containers

## Autoscaling

Requires **metrics-server** (applied in Jenkins Deploy stage). Verify:

```bash
kubectl get hpa -n capstone-app
```

CPU should show a percentage, not `<unknown>`.

## Deploy manually (without Jenkins)

```bash
aws eks update-kubeconfig --name devops-capstone --region ap-south-1
kubectl apply -f kubernetes/
```

## Rollback

```bash
kubectl rollout undo deployment/capstone-app -n capstone-app
kubectl rollout status deployment/capstone-app -n capstone-app
```

## Verify

```bash
kubectl get all -n capstone-app
curl http://$(kubectl get svc capstone-app -n capstone-app -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')/health
```

See [pipeline.md](pipeline.md) for Jenkins stage details.
