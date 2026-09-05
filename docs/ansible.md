# Ansible — Sprint 3

## Status: ready for Jenkins verification

## What this configures

After Terraform provisions the VPC and EKS cluster, Ansible configures the **Jenkins EC2 host** so it is ready for Sprint 4 deployment:

| Target | Connection | Packages / config |
|---|---|---|
| Jenkins EC2 | `localhost` (playbook runs on the Jenkins agent) | Docker, kubectl, AWS CLI, jq; `jenkins` user in `docker` group; kubeconfig for EKS |

EKS managed worker nodes are **not** configured over SSH — AWS manages their container runtime. The capstone requirement to install Docker and kubectl is satisfied on the Jenkins orchestrator host, which runs `docker build`, `kubectl apply`, and talks to the cluster API.

## Layout

```
ansible/
  ansible.cfg
  site.yml                 # main playbook + validation tasks
  inventory/hosts.yml      # localhost inventory for Jenkins host
  roles/
    common/                # Docker, kubectl, AWS CLI, jq
    jenkins/               # docker group, kubeconfig, cluster smoke test
```

## Running manually

From the Jenkins EC2 instance (after `terraform apply`):

```bash
cd ansible
EKS_CLUSTER=$(cd ../terraform && terraform output -raw eks_cluster_name)
ansible-playbook site.yml \
  -e aws_region=ap-south-1 \
  -e eks_cluster_name="$EKS_CLUSTER"
```

Dry-run syntax check (no changes applied):

```bash
ansible-playbook site.yml --check --diff \
  -e aws_region=ap-south-1 \
  -e eks_cluster_name=devops-capstone
```

## Jenkins integration

The `Ansible Configure` stage in `jenkins/Jenkinsfile` runs **immediately after** `Terraform Apply`:

1. Reads `eks_cluster_name` from Terraform outputs.
2. Installs Ansible on the Jenkins host (if missing).
3. Runs `ansible-playbook site.yml` with cluster name and region extra vars.
4. Validation play verifies `docker --version`, `kubectl version --client`, and `jenkins` ∈ `docker` group.

## Verify

```bash
# On Jenkins host after playbook run
docker --version
kubectl version --client
groups jenkins          # should include docker
sudo -u jenkins kubectl get nodes
```

Expected: kubectl lists 1–2 Ready nodes from the Terraform-managed node group.

## Troubleshooting

1. **`kubectl get nodes` AccessDenied** — Jenkins IAM role needs `eks:DescribeCluster` and an EKS access entry / `aws-auth` mapping for the instance role. This was resolved in Sprint 2; if policies were recently changed, wait ~60s for IAM propagation and retry.

2. **Docker permission denied for jenkins user** — the playbook adds `jenkins` to the `docker` group, but **existing Jenkins processes** may need a restart to pick up the new group membership: `sudo systemctl restart jenkins`.

3. **Corporate network / no direct SSH** — use SSM Session Manager to reach the Jenkins host (same workaround as Sprint 1).

## Definition of done

- [ ] Ansible stage runs automatically after Terraform in Jenkins pipeline
- [ ] Playbook is idempotent on re-run (second run shows few/no changes)
- [ ] `sudo -u jenkins kubectl get nodes` succeeds on Jenkins host
- [ ] Validation tasks pass (`docker`, `kubectl`, docker group)

## Next: Sprint 4

With kubeconfig and tooling in place on Jenkins, Sprint 4 adds `kubernetes/` manifests and a Deploy stage (`kubectl apply` + rollout status + smoke test).
