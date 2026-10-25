# Code and setup walkthrough (internal)

Read this **after** skimming [dev-setup-guide.md](dev-setup-guide.md) (what to click/run) and [project-walkthrough.md](project-walkthrough.md) (mental model). Here each layer is in **build order**, with **what the code does** and **how it connects to the next step**.

Suggested order: **Bootstrap → App → Terraform → Jenkins host → Pipeline stages → K8s → Monitoring**.

---

## Phase 0 — Manual AWS bootstrap (not in git)

These exist **before** the first green pipeline run. Nothing in the repo creates them automatically.

| Resource | Why | Referenced in code |
|----------|-----|-------------------|
| ECR repo `devops-capstone-app` | Store images Jenkins pushes | `jenkins/Jenkinsfile` `ECR_REPO` |
| S3 bucket + DynamoDB lock table | Remote Terraform state | `terraform/backend.tf` |
| Jenkins EC2 + instance profile | Runs the pipeline | Ansible `localhost`, Jenkins stages |
| IAM role for Jenkins (optional ARN) | EKS access after cluster recreate | `terraform/variables.tf` → `jenkins_role_arn` |

**Instance profile:** Jenkins calls `aws sts get-caller-identity`, ECR login, Terraform, and `aws eks update-kubeconfig` without access keys in git.

**`jenkins_role_arn`:** When Jenkins **creates** the cluster, EKS grants the creator admin. If the cluster is recreated and auth breaks, set `jenkins_role_arn` to the Jenkins EC2 role ARN so Terraform creates `aws_eks_access_entry` + `AmazonEKSClusterAdminPolicy` (see `terraform/modules/eks/main.tf`).

---

## Phase 1 — Application (`app/`)

The capstone app is intentionally small; the pipeline is the product.

### `app/app.py`

- **`/`** — JSON hello (smoke / demo).
- **`/health`** — Returns 200; used by Docker `HEALTHCHECK`, Kubernetes probes, and Jenkins smoke tests.
- **`/metrics`** — Prometheus text format (`app_requests_total`, `app_uptime_seconds`); scraped via pod annotations in `kubernetes/deployment.yaml`.

### `app/requirements.txt` + `app/tests/test_app.py`

- Pipeline **Test** stage creates a venv on the Jenkins host and runs `pytest -q` **before** Terraform (Sprint 7 fail-fast).

### `app/Dockerfile`

| Stage | Purpose |
|-------|---------|
| `build` | venv + `pip install -r requirements.txt` |
| `runtime` | slim image, non-root `appuser`, `gunicorn` on 8080 |
| `HEALTHCHECK` | hits `/health` inside the container |
| `docker build --pull` | Jenkins rebuilds on patched base images (Trivy) |

**Image naming:** Built locally as `devops-capstone-app:${IMAGE_TAG}`, tagged to `${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}` and `:latest` in **Push to ECR**.

---

## Phase 2 — Infrastructure as code (`terraform/`)

### Entry and state

**`terraform/backend.tf`**

- S3 backend + DynamoDB locking — team/state consistency for capstone.
- AWS provider `ap-south-1`, default tags `Project`, `Environment`, `ManagedBy`.

**`terraform/main.tf`**

- Wires two modules: `vpc` then `eks`.
- Passes subnet IDs, node sizing, and optional `jenkins_role_arn`.

**`terraform/variables.tf` / `outputs.tf`**

- Defaults: VPC `10.0.0.0/16`, 2 AZs, EKS `1.31`, nodes `t3.medium`, desired 2 (min 1, max 3).
- Outputs used by humans and Ansible/Jenkins: `eks_cluster_name`, `configure_kubectl` hint.

### VPC module (`terraform/modules/vpc/main.tf`)

1. **VPC** — DNS support/hostnames enabled.
2. **Public subnets** — `/24` per AZ, `map_public_ip_on_launch`, tags for ELB (`kubernetes.io/role/elb`).
3. **Private subnets** — offset CIDR, internal ELB tag.
4. **Single NAT gateway** — cost tradeoff; private nodes reach ECR/internet.
5. **Route tables** — public → IGW; private → NAT.

Workers run in **private** subnets; LoadBalancer Services use **public** subnets for AWS ELB.

### EKS module (`terraform/modules/eks/main.tf`)

1. **Cluster IAM role** + `AmazonEKSClusterPolicy`.
2. **`aws_eks_cluster.main`** — subnets = private + public; API public+private; `API_AND_CONFIG_MAP` auth; bootstrap creator admin.
3. **Node IAM role** — worker, CNI, ECR read-only attachments.
4. **`aws_eks_node_group.main`** — managed nodes in **private** subnets only; scaling min/max/desired from variables.
5. **Jenkins access (conditional)** — if `jenkins_role_arn` set: `aws_eks_access_entry` + cluster admin policy association.

Pipeline stages: **Terraform Init** → **validate** → **Plan** (`-detailed-exitcode`: 0=no change, 2=changes) → **Apply** only when `TF_CHANGES=true`.

---

## Phase 3 — Configuration management (`ansible/`)

Runs on the **Jenkins EC2 host** immediately after Terraform in the pipeline—not on EKS nodes.

### Inventory (`ansible/inventory/hosts.yml`)

- Host `localhost`, `ansible_connection: local` — playbook runs as part of Jenkins shell on the CI server.

### Playbook (`ansible/site.yml`)

1. Play **Configure Jenkins CI host** — roles `common`, `jenkins`.
2. Play **Validate** — `docker --version`, `kubectl version --client`, assert `jenkins` ∈ `docker` group.

### Role `common` (`ansible/roles/common/tasks/main.yml`)

- Apt packages (curl, jq, python tooling).
- **docker.io** installed and enabled.
- **AWS CLI v2** if missing (`get_url` + install script).
- **kubectl** pinned download (`v1.31.0` in tasks).

### Role `jenkins` (`ansible/roles/jenkins/tasks/main.yml`)

- Add **jenkins** user to **docker** group (pipeline runs Docker as jenkins).
- **`aws eks update-kubeconfig`** as `jenkins` user → `~/.kube/config`.
- **`kubectl get nodes`** — fails playbook if RBAC/network broken.

Pipeline passes `-e aws_region=... -e eks_cluster_name=$(terraform output -raw eks_cluster_name)`.

**Requires:** passwordless sudo for `jenkins` (manual one-time on EC2) so `become: true` works.

---

## Phase 4 — Kubernetes manifests (`kubernetes/`)

Applied in Jenkins **Deploy** stage after kubeconfig update.

### Order in pipeline

1. **metrics-server** (upstream YAML, version `METRICS_SERVER_VERSION` in Jenkinsfile) — HPA needs CPU metrics on EKS.
2. `namespace.yaml` → `deployment.yaml` → `service.yaml` → `hpa.yaml`.
3. **`kubectl set image`** — replaces placeholder tag with image built in **this** run (`BUILD_NUMBER`-`git sha`).

### `kubernetes/deployment.yaml`

- 2 replicas, resource requests/limits.
- **readinessProbe** / **livenessProbe** on `/health`.
- Pod annotations `prometheus.io/scrape`, `port`, `path` for Prometheus pod SD.
- Image in YAML is placeholder `latest`; real deploy is always pipeline `set image`.

### `kubernetes/service.yaml`

- **type: LoadBalancer** — AWS Classic/NLB hostname for public app URL (smoke test curls this).

### `kubernetes/hpa.yaml`

- CPU target 70%, min 2 max 5 replicas — needs metrics-server + pod CPU requests.

---

## Phase 5 — Monitoring (`monitoring/`)

Applied in Jenkins **Monitoring** stage (after smoke test).

| Manifest | Role |
|----------|------|
| `namespace.yaml` | `monitoring` namespace |
| `kube-state-metrics.yaml` | Cluster object metrics |
| `node-exporter.yaml` | Node hardware metrics (DaemonSet) |
| `prometheus-rbac.yaml` | SA + ClusterRole for pod/node SD |
| `prometheus-config.yaml` | Scrape jobs: self, pods (annotation filter), KSM, node-exporter; alert rules file mount |
| `prometheus.yaml` | Prometheus deployment |
| `grafana-dashboards.yaml` | ConfigMap dashboards |
| `grafana.yaml` | Grafana deployment (ClusterIP; port-forward for UI) |

**App metrics path:** Deployment annotations + `prometheus-config` `kubernetes-pods` job relabeling → scrape `capstone-app:8080/metrics`.

**Pipeline validation** curls `/metrics` and greps `app_requests_total`.

---

## Phase 6 — Jenkins pipeline (`jenkins/Jenkinsfile`)

Single declarative pipeline; source of truth for stage order.

### Global choices

| Setting | Code | Rationale |
|---------|------|-----------|
| `pollSCM('H/15 * * * *')` | triggers | Git poll without webhook setup |
| `disableConcurrentBuilds()` | options | One run at a time on single EC2 |
| `IMAGE_TAG` | env | Traceable deploy: build # + commit |
| ECR registry | Checkout script | No hardcoded account ID |
| Trivy / metrics-server versions | env | Reproducible scans and add-ons |

### Stage map (capstone task.md)

```
Checkout
  → Test → Build image → Scan image → Push to ECR     [Build]
  → Terraform Init → Plan → Apply (if changes)        [Infrastructure]
  → Ansible Configure                                 [Configuration]
  → Deploy → Post-deploy smoke test                     [Deployment]
  → Monitoring → Pipeline validation                    [Test & monitor]
```

### Notable implementation details

- **Scan image:** Trivy in Docker, CRITICAL only, `--ignore-unfixed`, exit 1 fails build before push.
- **Push to ECR:** `get-login-password` + dual tag `:tag` and `:latest`.
- **Smoke test:** Poll LB hostname, wait for DNS, retry `curl /health`.
- **post.always:** `docker image prune` — disk on Jenkins host.
- **post.failure:** Optional Slack via credential `slack-webhook-url`.

---

## Phase 7 — How a full run feels (timeline)

1. **Checkout** — clone repo; compute ECR URL from STS.
2. **CI block (~minutes)** — pytest, build, Trivy, push. If fail, **no Terraform cost/time**.
3. **Terraform** — first run ~15 min (VPC+EKS); later runs often **Apply skipped** if plan empty.
4. **Ansible** — minutes; idempotent package/kubeconfig refresh.
5. **Deploy** — metrics-server + manifests + rolling update to new image.
6. **Smoke** — wait for ELB + HTTP (can be several minutes).
7. **Monitoring** — stack apply + rollout status.
8. **Validation** — kubectl checks + health + metrics grep.

---

## File index (quick lookup)

| Path | One line |
|------|----------|
| `app/app.py` | Flask routes health + metrics |
| `app/Dockerfile` | Multi-stage non-root image |
| `terraform/main.tf` | VPC + EKS modules |
| `terraform/modules/vpc/main.tf` | Network, NAT, subnet tags |
| `terraform/modules/eks/main.tf` | Cluster, node group, Jenkins access entry |
| `terraform/backend.tf` | S3 state + provider |
| `ansible/site.yml` | Host configure + validate |
| `ansible/roles/common/` | Docker, AWS CLI, kubectl |
| `ansible/roles/jenkins/` | jenkins user, kubeconfig, node check |
| `kubernetes/*.yaml` | App deploy, LB, HPA |
| `monitoring/*.yaml` | Prometheus/Grafana stack |
| `jenkins/Jenkinsfile` | Full CI/CD orchestration |

---

## What to read in the repo next

1. Skim entire `jenkins/Jenkinsfile` once with this doc open.
2. Trace one variable: `IMAGE_TAG` from Test through Push, Deploy `set image`, success echo.
3. Trace one metric: `app.py` `/metrics` → deployment annotations → `prometheus-config.yaml` → validation grep.
4. Public deep dives: [pipeline.md](../pipeline.md), [terraform.md](../terraform.md), [ansible.md](../ansible.md), [kubernetes.md](../kubernetes.md), [monitoring.md](../monitoring.md), [sprint-7.md](../sprint-7.md).

For viva phrasing, pair this with [interview-qa.md](interview-qa.md) and [live-demo-guide.md](live-demo-guide.md).
