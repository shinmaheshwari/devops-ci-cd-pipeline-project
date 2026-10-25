# Dev setup guide (internal)

Step-by-step to reproduce the environment from zero. Public runbooks: [jenkins.md](../jenkins.md), [terraform.md](../terraform.md).

## 1. AWS one-time bootstrap

| Step | Action | Doc |
|------|--------|-----|
| Region | Use `ap-south-1` everywhere | [architecture.md](../architecture.md) |
| ECR | Create repo `devops-capstone-app` | [sprint-1.md](../sprint-1.md) |
| S3 + DynamoDB | State bucket `devops-capstone-tfstate-<account>` + lock table | [terraform.md](../terraform.md) |
| IAM | Jenkins role `jenkins-capstone-role` + profile `jenkins-capstone-profile` | [jenkins.md](../jenkins.md) |

## 2. Jenkins EC2 (manual, survives `terraform destroy`)

Follow [jenkins.md](../jenkins.md) — build the host from scratch:

1. Launch `t3.medium`, Ubuntu 22.04, 20 GB, default VPC, SG restricted to your IP (22, 8080).
2. Attach instance profile with ECR, SSM, and broad Terraform permissions (capstone tradeoff).
3. Java 21 + Jenkins LTS (2026 apt key).
4. Docker; add `jenkins` to `docker` group.
5. Passwordless sudo for `jenkins` (Ansible stage).
6. Install Terraform on the host; avoid broken HashiCorp apt sources.
7. Access UI via **SSM port-forward** if corporate network blocks direct 8080.

## 3. Jenkins job

| Setting | Value |
|---------|--------|
| Type | Pipeline from SCM |
| Repo | This GitHub repository |
| Branch | `*/main` |
| Script path | `jenkins/Jenkinsfile` |
| Credential | `slack-webhook-url` (Secret text, optional) |

Triggers: `pollSCM` in Jenkinsfile — [jenkins-triggers.md](../jenkins-triggers.md).

**Important:** Disable the job while EKS is destroyed, or the next poll will recreate infra.

## 4. First pipeline run

1. Run job manually on `main`.
2. **Test → Build → Scan → Push** must pass before Terraform.
3. Terraform creates VPC + EKS (~15 min first time).
4. Ansible configures host tooling.
5. Deploy + smoke test + monitoring + validation.

Verify: [e2e-testing.md](../e2e-testing.md).

## 5. Local developer machine (optional)

```bash
cd app && docker build -t app:local . && pytest -q
cd terraform && terraform init && terraform validate
aws eks update-kubeconfig --name devops-capstone --region ap-south-1
kubectl get nodes
```

Provider lock platforms: `linux_amd64` (Jenkins) and `darwin_arm64` (Mac) — [sprint-7.md](../sprint-7.md).

## 6. Teardown

```bash
cd terraform && terraform destroy
```

Stop Jenkins EC2 when idle. See [cost-optimization.md](../cost-optimization.md).
