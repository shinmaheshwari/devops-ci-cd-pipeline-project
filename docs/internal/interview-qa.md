# Interview / viva Q&A (internal)

Short answers tied to **this** repo. Expand with your own examples.

## Architecture

**Q: Describe the architecture in one minute.**  
A: Developer pushes to GitHub; Jenkins on EC2 runs a declarative pipeline — tests and Trivy scan, pushes to ECR, Terraform provisions VPC/EKS with S3 state, Ansible prepares the Jenkins host, kubectl deploys the Flask app with HPA and LoadBalancer, then Prometheus/Grafana monitor app and nodes. See [architecture.md](../architecture.md).

**Q: Why Jenkins on EC2 instead of in EKS?**  
A: Capstone bootstrap — Jenkins exists before the cluster and survives `terraform destroy`; simpler for a single-tenant demo.

**Q: Public vs private subnets?**  
A: EKS nodes in private subnets; NAT for outbound; LoadBalancer Service exposes the app; Jenkins in default VPC (manual).

## Terraform vs Ansible

**Q: Difference between Terraform and Ansible?**  
A: Terraform creates cloud resources (VPC, EKS, IAM) with declarative state in S3. Ansible configures the OS on the Jenkins server (packages, kubeconfig) after infra exists.

**Q: Why is Jenkins EC2 not in Terraform?**  
A: Avoid destroying/recreating the CI server with `terraform destroy`; documented tradeoff in [terraform.md](../terraform.md).

## Pipeline

**Q: Why run tests before Terraform (Sprint 7)?**  
A: Fail fast — broken code should not trigger a 10–15 minute `terraform apply`.

**Q: What does Trivy do here?**  
A: Scans the built image; pipeline fails on unfixed CRITICAL CVEs before ECR push.

**Q: When does Terraform Apply run?**  
A: After plan; Apply executes only if plan detects changes (`-detailed-exitcode` pattern).

**Q: How is the deployed image tag chosen?**  
A: `BUILD_NUMBER`-`git commit`; `kubectl set image` in Deploy stage.

## Kubernetes

**Q: Liveness vs readiness?**  
A: Both hit `/health`; readiness gates traffic, liveness restarts unhealthy pods ([kubernetes.md](../kubernetes.md)).

**Q: Why metrics-server?**  
A: Not included on EKS by default; HPA needs real CPU metrics.

**Q: How does the app scale?**  
A: HPA on CPU 70%, min 2 max 5 replicas; cluster nodes 1–3 via managed node group.

## IAM & EKS access

**Q: How does Jenkins talk to EKS?**  
A: EC2 instance role; Jenkins runs Terraform as cluster creator; kubeconfig for kubectl on the host ([terraform.md](../terraform.md), [sprint-7.md](../sprint-7.md)).

**Q: Instance profile vs access keys?**  
A: Instance profile — no long-lived keys in Jenkins or git.

## Monitoring

**Q: What metrics do you collect?**  
A: App `/metrics`, kube-state-metrics, node-exporter; alerts in Prometheus config ([monitoring.md](../monitoring.md)).

**Q: Why Grafana port-forward?**  
A: Service is ClusterIP; dev password in manifests — avoid public exposure.

## Cost & ops

**Q: How do you control cost?**  
A: Single NAT, small instances, `terraform destroy` when idle, stop Jenkins EC2 — [cost-optimization.md](../cost-optimization.md).

**Q: What happens if pollSCM runs while cluster is down?**  
A: Pipeline may recreate infra — disable job when torn down ([sprint-6.md](../sprint-6.md)).

## DevOps culture

**Q: What would you improve for production?**  
A: Least-privilege IAM, separate Terraform role, Alertmanager, ALB+Ingress+TLS, Cluster Autoscaler/Karpenter, native S3 locking, manual approval before apply, secrets in AWS Secrets Manager.
