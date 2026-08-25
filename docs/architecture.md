# Architecture

## Overview

Git push triggers Jenkins (running on an EC2 host), which builds and pushes a
Docker image to ECR, provisions/updates AWS infra with Terraform, configures
hosts with Ansible, deploys to EKS via `kubectl`, and the app is then observed
via Prometheus + Grafana running in-cluster.

```
Developer --push--> GitHub --webhook/poll--> Jenkins (EC2)
                                                 |
                          -----------------------+-----------------------
                          |            |            |            |
                     Docker build   Terraform    Ansible      kubectl
                          |          (VPC/EKS/     (host       apply
                          v           IAM/S3)      config)        |
                        ECR                                       v
                          |                                 EKS Cluster
                          +------------------image pull---------->|
                                                                   |
                                                        App Deployment + Service
                                                        HPA (CPU-based, 2-5 pods)
                                                        Prometheus + Grafana
```

## Network layout

- 1 VPC, 2 Availability Zones
- Public subnets: NAT gateway, Jenkins EC2 (SSH restricted to my IP only), ALB/LoadBalancer for app ingress
- Private subnets: EKS worker nodes (no direct public IP)
- Single NAT gateway (cost optimization — acceptable for a dev/demo cluster, would be one-per-AZ in production)

## IAM boundaries

| Identity | Scope |
|---|---|
| Jenkins EC2 instance role | ECR push/pull, `eks:DescribeCluster` + node/RBAC access to the target cluster, S3 + DynamoDB access scoped to the Terraform state bucket/table, no broad `*` permissions |
| EKS cluster role | Standard AWS-managed EKS cluster policy |
| EKS node group role | `AmazonEKSWorkerNodePolicy`, `AmazonEKS_CNI_Policy`, `AmazonEC2ContainerRegistryReadOnly` |

## Components

| Component | Purpose | Provisioned by |
|---|---|---|
| Jenkins (EC2) | CI/CD orchestrator | Sprint 1 (manual/minimal TF), owned by Terraform from Sprint 2 |
| ECR | Container image registry | Sprint 1 |
| VPC / subnets / NAT / IGW | Network | Sprint 2 (Terraform) |
| EKS cluster + node group | App + monitoring compute | Sprint 2 (Terraform) |
| S3 + DynamoDB | Terraform remote state + locking | Sprint 2 |
| App Deployment/Service/HPA | Runs the app | Sprint 4 (kubectl via Jenkins) |
| Prometheus + Grafana | Observability | Sprint 5 |

## Region

`ap-south-1` (Mumbai) — pick one and keep every resource in it for this project.
