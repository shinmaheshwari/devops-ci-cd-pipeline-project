# Pipeline — Sprint 4

## Status: complete — verified end-to-end, live app reachable via LoadBalancer

## Stage diagram

```
Checkout -> Terraform (Init/Plan/Apply) -> Ansible Configure -> Test -> Build -> Push to ECR -> Deploy -> Smoke test
```

## What Deploy does

1. `aws eks update-kubeconfig` — points kubectl at the current cluster
2. Applies `metrics-server` (idempotent) — **not included by default on EKS**,
   required for HPA to report real CPU numbers instead of `<unknown>`
3. Applies `kubernetes/*.yaml` (namespace, deployment, service, hpa)
4. `kubectl set image` — swaps in the image tag just built/pushed this run,
   rather than whatever's checked into `deployment.yaml`
5. `kubectl rollout status` — waits for the rollout to actually finish
6. Smoke test stage polls for the LoadBalancer hostname (up to 5 min) then
   curls `/health` through the real public endpoint

## Rollback

```bash
kubectl rollout undo deployment/capstone-app -n capstone-app
kubectl rollout status deployment/capstone-app -n capstone-app
```

## Verifying it worked

```bash
kubectl get pods -n capstone-app        # both replicas Running, 1/1
kubectl get hpa -n capstone-app         # cpu: X%/70%, not <unknown>
kubectl get svc capstone-app -n capstone-app   # LoadBalancer hostname assigned
curl http://<hostname>/health
```

## Lessons learned

1. **Metrics Server is not part of default EKS.** HPA will show `<unknown>`
   for CPU targets indefinitely without it — no error, just silently useless
   autoscaling. Installing it as an idempotent step inside the Deploy stage
   (rather than a one-time manual setup step someone has to remember) means
   it's automatically present on every fresh cluster, including after a
   destroy/recreate cycle.

2. **A stale Jenkins job Branch Specifier caused several "successful" but
   wrong builds.** Back in Sprint 3, the job was pointed at `*/sprint3-review`
   to test that PR branch before merging — and never switched back to
   `*/main` afterward. Every subsequent build kept quietly rebuilding the old
   branch, showing `SUCCESS` with the *old* pipeline stages and post-message
   (`"Infra applied and pushed..."` instead of the new `"Deployed ... to
   EKS"`), which looked like a real result but was stale. The tell was
   comparing the commit hash in the image tag against the latest commit on
   `main` — worth checking that match any time a build's behavior doesn't
   match what was just pushed.

3. **EKS access entries don't survive `terraform destroy` / recreate**, even
   for the Jenkins role (which IS managed by Terraform and gets its access
   entry recreated automatically) — but the *cluster creator's* own access
   depends on `bootstrap_cluster_creator_admin_permissions`, which wasn't set.
   This caused the exact same "must be logged in to the server" error twice,
   on two separate destroy/recreate cycles, before being fixed by adding
   `bootstrap_cluster_creator_admin_permissions = true` to the cluster's
   `access_config` block — worth remembering that a fix flagged as a
   "follow-up, not yet addressed" in one sprint's docs is a real, recurring
   cost if left unaddressed into the next.

## Next: Sprint 5

Prometheus + Grafana for cluster/app observability, plus Jenkins failure
notifications.
