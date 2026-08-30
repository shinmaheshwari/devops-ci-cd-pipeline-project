# Terraform — Sprint 2

## Status: complete

## What this provisions

- VPC (`10.0.0.0/16`) across 2 AZs (`ap-south-1a`, `ap-south-1b`)
- 2 public + 2 private subnets, 1 NAT gateway (single NAT — cost tradeoff, see below)
- EKS cluster `devops-capstone` (Kubernetes 1.31)
- Managed node group: 2× `t3.medium`, scales 1-3
- All required IAM roles (cluster role, node role with worker/CNI/ECR-readonly policies)

## Remote state backend

- S3 bucket: `devops-capstone-tfstate-562904760755` (versioned, public access blocked)
- DynamoDB table: `devops-capstone-tflock` (state locking)
- Bootstrapped manually once via AWS CLI, before any `terraform init` — this is
  intentional, since Terraform can't manage the backend it depends on to store
  its own state.

## Variables

All defined in `variables.tf` with sensible defaults — the only ones likely worth
changing for a different environment:

| Variable | Default | Notes |
|---|---|---|
| `aws_region` | `ap-south-1` | Keep consistent across all resources |
| `node_instance_type` | `t3.medium` | Balance of cost vs capacity for a demo cluster |
| `node_min_size` / `node_max_size` | 1 / 3 | HPA-friendly range without runaway cost |

## Running it

```bash
cd terraform
terraform init      # connects to S3 backend
terraform validate  # syntax check, no AWS calls
terraform plan       # shows what would change
terraform apply      # actually creates/updates infra
```

Also runs automatically from Jenkins (`jenkins/Jenkinsfile`, stages: Terraform Init →
Plan → Apply), using the EC2 instance's IAM role — no stored AWS credentials in Jenkins.

## Destroy / rollback

```bash
cd terraform
terraform destroy
```

**Important for cost control:** unlike the EC2 instance (which can be stopped for
near-zero cost), the EKS control plane bills continuously (~$0.10/hr) while it
exists — there's no "stop" option, only destroy/recreate. Destroy after each work
session if not actively using the cluster, and recreate at the start of the next
one (`terraform apply` — about 10-15 min to rebuild from scratch, all captured in
code so nothing is lost).

## Estimated monthly cost (if left running continuously)

| Resource | Approx. cost |
|---|---|
| EKS control plane | ~$73/month |
| 2× t3.medium nodes | ~$60/month |
| NAT gateway | ~$32/month + data |
| EBS volumes, EIP | ~$5/month |
| **Total** | **~$170/month** |

Destroying between sessions is the main lever for keeping this near zero during
development.

## Lessons learned

1. **`AmazonEKSClusterPolicy` / `AmazonEKSServicePolicy` are for the cluster's own
   service role, not for a caller managing the cluster via API.** Jenkins (as the
   Terraform-executing role) needed a separate, explicit `eks:*` permission to call
   `DescribeCluster` / `DescribeNodegroup` — attaching the cluster-facing policies to
   the Jenkins role did nothing useful. Fixed with a custom inline policy
   (`eks-caller-access`) granting `eks:*` on `*`.

2. **`AmazonVPCFullAccess` doesn't cover every EC2-level action** — specifically
   `ec2:DescribeAddressesAttribute` on Elastic IPs required the broader
   `AmazonEC2FullAccess` instead.

3. **IAM policy attachment is not instantly visible to an already-running EC2
   instance's assumed-role session.** Twice, a newly attached policy caused a
   `403`/`AccessDenied` on the very next command, which resolved itself after
   waiting ~30-60 seconds and retrying — not a configuration error, just
   eventual-consistency propagation delay.

4. **Broad IAM permissions used here as a pragmatic tradeoff**: the Jenkins role
   currently has `IAMFullAccess`, `S3FullAccess`, `EC2FullAccess`, and `eks:*` —
   effectively full infrastructure control. Acceptable for a single-user capstone
   project, but in a production setting this would be split into a dedicated,
   narrowly-scoped Terraform execution role (least-privilege per resource type)
   separate from the general Jenkins host role.

## Definition of done

- [x] Two consecutive Jenkins-driven `terraform apply` runs succeed without drift
- [x] `aws eks describe-cluster` / `kubectl get nodes` show a healthy cluster
- [x] Terraform fully wired into the Jenkins pipeline (Init → Plan → Apply stages)

