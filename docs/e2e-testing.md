# End-to-end testing

Checklist after a full Jenkins run: **git push → ECR → EKS app → monitoring**.


## Preconditions

- Jenkins job `capstone-build`: **Pipeline from SCM**, `jenkins/Jenkinsfile`, branch `*/main`
- EC2 instance profile (no AWS keys in git)
- Credential `slack-webhook-url` optional — [monitoring.md](monitoring.md)

## Automated coverage in Jenkins

| Stage | Validates |
|-------|-----------|
| Test | `pytest` (`app/tests/`) |
| Scan image | Trivy — blocks CRITICAL (see [sprint-7.md](sprint-7.md)) |
| Push to ECR | Image tagged `BUILD_NUMBER`-`commit` |
| Terraform Apply | Infra when plan has changes |
| Post-deploy smoke test | Public LB `/health` |
| Pipeline validation | Deploy/HPA/monitoring pods; `/metrics` on app |

## Manual verification

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
# Targets: app pods, kube-state-metrics, node-exporter UP
kubectl port-forward svc/grafana -n monitoring 3000:80
```

### 4. HPA

```bash
kubectl get hpa -n capstone-app
```

### 5. Rollback (optional)

```bash
kubectl rollout undo deployment/capstone-app -n capstone-app
```

## Failure scenarios

| Symptom | Doc |
|---------|-----|
| HPA CPU `<unknown>` | [pipeline.md](pipeline.md) |
| Wrong pipeline / old image tag | [jenkins.md](jenkins.md) |
| kubectl unauthorized | [terraform.md](terraform.md) |
| Trivy / scan failure | [sprint-7.md](sprint-7.md) |
| Ansible sudo/apt errors | [jenkins.md](jenkins.md), [ansible.md](ansible.md) |

## Sign-off

- [ ] Full pipeline green through **Pipeline validation**
- [ ] Manual steps above verified
- [ ] Presenter rehearsal (internal demo guide) completed
