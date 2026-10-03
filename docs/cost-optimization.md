# Cost optimization (capstone — 10% evaluation)

This project targets a **dev/demo** budget, not production HA. Choices below keep spend predictable and teardown simple.

## Design choices that save money

| Choice | What we did | Production alternative |
|--------|-------------|-------------------------|
| NAT gateway | **Single** NAT in one AZ | NAT per AZ for HA |
| EKS nodes | `t3.medium`, 1–3 nodes (desired 2) | Larger types, more nodes |
| Jenkins | One `t3.medium` EC2 (Sprint 1) | Managed CI (CodePipeline, etc.) |
| LoadBalancers | App + Grafana LB (demo access) | Ingress + single ALB |
| State | S3 + DynamoDB lock (minimal objects) | Same pattern, often shared bucket |
| Pipeline | Full Terraform on every run | Separate infra job on schedule |

## Rough monthly cost (`ap-south-1`, everything running)

| Resource | Approx. USD/month |
|----------|-------------------|
| EKS control plane | ~$73 |
| 2× `t3.medium` worker nodes | ~$60 |
| NAT gateway + data | ~$32+ |
| Jenkins EC2 `t3.medium` | ~$30 |
| EBS, EIPs, ECR storage | ~$5–15 |
| **Total (always on)** | **~$200–220** |

See also [terraform.md](terraform.md#estimated-monthly-cost-if-left-running-continuously).

## Teardown workflow (recommended during development)

EKS control plane bills **24/7** until destroyed — there is no “stop cluster” option.

```bash
cd terraform
terraform destroy   # removes VPC, EKS, nodes (Jenkins EC2 is manual unless imported)
```

- **Stop Jenkins EC2** when not demoing (saves compute; EBS still billed).
- **Keep ECR images** — storage is cheap; speeds rebuilds.
- **Keep S3 state bucket** — required for team Terraform; versioning adds minor cost.

## Autoscaling and right-sizing

- **HPA** (`kubernetes/hpa.yaml`): min 2, max 5 replicas on CPU 70% — avoids idle over-provisioning while allowing load demos.
- **Node group** (`node_min_size` 1, `max` 3): cluster can shrink to one node off-peak if you lower desired count manually or via cluster autoscaler (not installed in this capstone).

## Tags

All Terraform-managed resources use:

`Project=devops-capstone`, `Environment=dev`, `ManagedBy=terraform`

Use AWS Cost Explorer filtered by `Project` to audit spend.

## Viva talking points

1. Single NAT is the largest **conscious** HA tradeoff.
2. Destroy-between-sessions is the main **operational** cost lever for students.
3. Broad Jenkins IAM was accepted for speed; production would use a dedicated Terraform role with least privilege.
