# Ansible — Sprint 3

## Status: complete — verified end-to-end via Jenkins pipeline

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

- [x] Ansible stage runs automatically after Terraform in Jenkins pipeline
- [x] Playbook completes successfully on the Jenkins host, in-pipeline
- [x] `kubectl get nodes` succeeds from the Jenkins host (verified via EKS access entry)
- [x] Validation tasks pass (`docker`, `kubectl`, docker group)

## Lessons learned

None of these were visible from reading the code — all four surfaced only once
the playbook was actually run through Jenkins end-to-end, which is exactly why
that verification step mattered before merging.

1. **EKS access entries need `access_config` explicitly set on the cluster.**
   The PR added `aws_eks_access_entry` / `aws_eks_access_policy_association`
   resources for the Jenkins role, but the `aws_eks_cluster` resource had no
   `access_config` block, so the cluster defaulted to `CONFIG_MAP`-only
   authentication mode. AWS rejected the access-entry creation with
   `InvalidRequestException: The cluster's authentication mode must be set to
   one of [API, API_AND_CONFIG_MAP]`. Fixed by adding:
   ```hcl
   access_config {
     authentication_mode = "API_AND_CONFIG_MAP"
   }
   ```
   to `terraform/modules/eks/main.tf`. `API_AND_CONFIG_MAP` (rather than plain
   `API`) was chosen to stay backward-compatible with any existing
   `aws-auth` ConfigMap approach.

   **Follow-up not yet addressed:** the cluster creator (whoever runs
   `terraform apply`) isn't automatically granted cluster-admin access unless
   `bootstrap_cluster_creator_admin_permissions = true` is also set inside
   `access_config`. This wasn't blocking (the applying user got a manual
   access entry via AWS CLI during testing), but should be added so a new
   teammate running `apply` for the first time isn't locked out of their own
   cluster.

2. **The `jenkins` system user had no sudo access.** The Ansible playbook
   (via the Jenkinsfile's `Ansible Configure` stage) needs root to install
   packages and configure the host, but nothing — not the PR, not the
   original Sprint 1 setup — ever granted the `jenkins` user sudo rights.
   `TASK [Gathering Facts]` failed immediately with `sudo: a password is
   required`. Fixed with a dedicated sudoers file:
   ```bash
   echo "jenkins ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/jenkins-ansible
   sudo chmod 440 /etc/sudoers.d/jenkins-ansible
   ```
   **Known trade-off:** this grants the `jenkins` user (and therefore any
   pipeline code running as it) unrestricted, passwordless root access. That's
   acceptable for a personal capstone host, but in a production setup this
   kind of config-management work would typically run in an isolated,
   ephemeral build agent rather than directly on a long-lived host with this
   level of access.

3. **A stale manually-added apt source broke Ansible's `apt` module.** The
   HashiCorp apt repo (added manually in Sprint 2 to install Terraform) had an
   expired GPG key. Plain `apt-get update` just warns and continues using the
   old cache — but Ansible's `apt` module treats any repo failure as fatal
   when refreshing the cache, so the `common : Install base packages` task
   failed with `Failed to update apt cache: unknown reason`, giving no hint
   that the actual cause was one broken, unrelated repo. Fixed by removing the
   stale source:
   ```bash
   sudo rm -f /etc/apt/sources.list.d/hashicorp.list
   ```
   Worth remembering: any manually-added apt source with a signing key is a
   latent trap for future automation on the same host, since it can silently
   break well after the fact when the key expires.

4. **`set -euo pipefail` silently fails without `executable: /bin/bash`.**
   The "Unpack and install AWS CLI" task used `ansible.builtin.shell` with a
   bash-specific `set -euo pipefail` line, but Ansible's `shell` module
   defaults to `/bin/sh` (dash on Ubuntu), which doesn't support the
   `pipefail` option — failing with `set: Illegal option -o pipefail`. Fixed
   by adding `executable: /bin/bash` under the task's `args:`.

## Next: Sprint 4

With kubeconfig and tooling in place on Jenkins, Sprint 4 adds `kubernetes/`
manifests and a Deploy stage (`kubectl apply` + rollout status + smoke test).
