# Project 4 — Sprint reference and finalization

Authoritative requirements: [docs/task.md](../../../docs/task.md).

Evaluation: Documentation 15% · Implementation 75% · Cost optimization 10%.

---

## Jenkins pipeline stages (end state)

| Stage | Capstone expectation |
|-------|---------------------|
| Build | Git trigger → Docker build → push to ECR |
| Infrastructure | Terraform apply (VPC, EKS, EC2) → state in S3 |
| Configuration | Ansible after Terraform → Docker, kubectl, deps on nodes/EC2 |
| Deploy | kubectl apply manifests → Service, health checks, HPA |
| Test & monitor | Post-deploy tests → Prometheus/Grafana/alerts |

---

## Sprint 1 — Architecture, Docker, Jenkins

### Checklist

- [ ] Architecture diagram (VPC, public/private subnets, EKS, Jenkins EC2, ECR, monitoring)
- [ ] Sample web app in `app/`
- [ ] `Dockerfile` (prefer multi-stage); image builds locally
- [ ] ECR repository; image pushed successfully
- [ ] Jenkins on EC2; plugins: Docker, Kubernetes, AWS CLI
- [ ] Jenkins IAM/credentials for EKS and AWS APIs
- [ ] Git webhook or poll SCM triggers a test build
- [ ] `docs/` sprint-1 notes (setup, access, diagram path)

### Artifacts

`app/`, `docs/architecture.*`, Jenkins access URL, ECR image URI

### Definition of done

- Jenkins reaches EKS/APIs with assumed role or scoped credentials
- Pipeline or freestyle job builds image and pushes to ECR
- Architecture documented and reviewed

### Verify

```bash
docker build -t <app> ./app
aws ecr describe-repositories
# On Jenkins: test build + ECR push
kubectl get nodes   # from Jenkins agent or EC2 with configured kubeconfig
```

---

## Sprint 2 — Terraform + Jenkins infra job

### Checklist

- [ ] Terraform modules: VPC, subnets, security groups, EKS, EC2 (Jenkins if not existing)
- [ ] S3 backend + DynamoDB (or equivalent) for state lock
- [ ] Jenkins job/pipeline stage runs `terraform plan/apply`
- [ ] State stored in S3; no local-only state for shared envs
- [ ] Idempotent re-run tested
- [ ] `docs/` Terraform variables, backend setup, rollback notes

### Artifacts

`terraform/`, Jenkins Terraform job, S3 state bucket name in docs

### Definition of done

- `terraform apply` from Jenkins provisions consistent infra twice without drift errors
- Team can collaborate via remote state

### Verify

```bash
cd terraform && terraform init && terraform validate
# Jenkins job log shows successful apply
aws eks describe-cluster --name <cluster>
```

---

## Sprint 3 — Ansible + Jenkins integration

### Checklist

- [ ] Playbooks: Docker, kubectl, dependencies on target hosts
- [ ] Jenkins stage runs after Terraform stage (pipeline order)
- [ ] Inventory/dynamic inventory or tags for Terraform-created hosts
- [ ] Playbooks tested on Terraform-provisioned hosts
- [ ] `docs/` Ansible inventory and run instructions

### Artifacts

`ansible/`, Jenkinsfile stage or chained job, sample playbook run output in docs

### Definition of done

- Ansible runs automatically after infra provision; hosts match expected config (docker version, kubectl works)

### Verify

```bash
ansible-playbook -i <inventory> site.yml --check  # then full run
ssh <host> 'docker --version && kubectl version --client'
```

---

## Sprint 4 — CI/CD deploy to EKS

### Checklist

- [ ] Declarative Jenkinsfile: build → test → push ECR → deploy
- [ ] Kubernetes Deployment + Service (LoadBalancer or Ingress per design)
- [ ] Liveness and readiness probes
- [ ] HPA configured
- [ ] End-to-end: git push → running app on EKS
- [ ] `docs/` pipeline diagram and rollback steps

### Artifacts

`jenkins/Jenkinsfile`, `kubernetes/*.yaml`, deployed app URL

### Definition of done

- Code change triggers full path to updated pods on EKS
- Health checks pass; scaling policy documented

### Verify

```bash
kubectl get deploy,svc,hpa -n <namespace>
curl <service-endpoint>
# Trigger Jenkins build from sample commit
```

---

## Sprint 5 — Prometheus, Grafana, alerts

### Checklist

- [ ] Prometheus scrapes app and node metrics in EKS
- [ ] Grafana dashboards (app + cluster health)
- [ ] Alert rules for critical metrics (pod crash, high CPU, failed deploy signal)
- [ ] Jenkins failure notifications (email/Slack/webhook as chosen)
- [ ] `docs/` dashboard URLs, alert runbook

### Artifacts

`monitoring/` manifests or Helm values, Grafana dashboard JSON export optional

### Definition of done

- Metrics visible in Grafana; test alert fires on simulated failure
- Jenkins job failure visible to operators

### Verify

```bash
kubectl get pods -n monitoring
# Port-forward Grafana; confirm targets UP in Prometheus
```

---

## Sprint 6 — Testing, documentation, production readiness

### Checklist

- [ ] Automated tests in pipeline (unit/smoke as appropriate)
- [ ] End-to-end test doc: infra + deploy + monitor
- [ ] Full documentation: Terraform, Ansible, Jenkins, Kubernetes, monitoring
- [ ] Automated triggers wired (SCM → build → deploy chain)
- [ ] Cost section in docs (instance sizes, autoscaling, cleanup)
- [ ] Viva/demo script: 5–10 min walkthrough of pipeline stages

### Artifacts

`docs/` complete runbooks, test results, known limitations

### Definition of done

- All five Jenkins stages run unattended from a sample commit
- Documentation sufficient for another engineer to reproduce
- Cost optimizations documented

### Verify

- Dry-run full pipeline on clean branch
- Peer-style review: can someone follow docs only and reach deployed app?

---

## Full project deliverables (capstone sign-off)

- [ ] End-to-end Jenkins pipeline (all stages)
- [ ] Terraform-managed AWS infra (VPC, EKS, EC2, S3 state)
- [ ] Ansible configuration management integrated in pipeline
- [ ] Application on EKS with scaling and health checks
- [ ] Prometheus + Grafana + alerts
- [ ] Comprehensive `docs/` (setup, usage, troubleshooting, cost)

---

## Finalization prompts (for the agent)

When the user asks to **finalize**:

1. Scan repo for artifacts above; list gaps by sprint.
2. Pick the lowest incomplete sprint unless the user specifies otherwise.
3. Implement the smallest set of changes to satisfy that sprint’s definition of done.
4. Run verification commands; report pass/fail.
5. Suggest doc updates and viva talking points for completed sprints.

Do not claim project complete until **Full project deliverables** are all checked with evidence.
