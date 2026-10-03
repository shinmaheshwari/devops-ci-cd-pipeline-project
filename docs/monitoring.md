# Monitoring — Sprint 5

## Status: implemented — verify targets, dashboard, and alerts after Jenkins run

## What gets deployed

| Component | Namespace | Purpose |
|---|---|---|
| Prometheus | `monitoring` | Scrapes app pods, kube-state-metrics, node-exporter |
| kube-state-metrics | `monitoring` | Cluster object metrics (pods ready, deployments, etc.) |
| node-exporter | `monitoring` | **Node** CPU/memory (DaemonSet on workers) |
| Grafana | `monitoring` | LoadBalancer UI, datasource + **Capstone — App & Cluster** dashboard |
| Alert rules | Prometheus config | App down, high request rate, high node CPU |

The Jenkins **Monitoring** stage applies all `monitoring/*.yaml` files after the app smoke test.

## Grafana dashboard

Provisioned automatically: folder **Capstone** → **Capstone — App & Cluster**

Panels include app scrape up-count, request rate, ready pods (kube-state-metrics), and node CPU %.

```bash
kubectl get svc grafana -n monitoring
# http://<EXTERNAL-IP>/ — login admin / capstone-dev (dev-only)
```

Screenshot for submission: [docs/screenshots/README.md](screenshots/README.md) (`sprint5-grafana-dashboard.png`).

## Verify Prometheus targets

```bash
kubectl port-forward svc/prometheus -n monitoring 9090:9090
# http://localhost:9090/targets
# Expect UP: kubernetes-pods (capstone-app), kube-state-metrics, node-exporter
```

## Alert runbook

| Alert | Meaning | Test |
|-------|---------|------|
| `CapstoneAppDown` | Cannot scrape app pods | `kubectl scale deploy/capstone-app -n capstone-app --replicas=0`, wait 2m, check Prometheus **Alerts** |
| `CapstoneHighRequestRate` | Demo threshold exceeded | Load-test or lower threshold temporarily |
| `NodeHighCPU` | Worker CPU > 85% for 10m | Stress node or adjust threshold |

Alerts appear in Prometheus UI (**Alerts** tab). Alertmanager routing is not deployed — add Alertmanager + Slack in a future iteration.

## Jenkins failure notifications

On pipeline **failure**, Jenkins:

1. Logs guidance to check Grafana/Prometheus.
2. If job environment variable **`SLACK_WEBHOOK_URL`** is set (Incoming Webhook URL), posts a JSON message via `curl`.

Configure in Jenkins → job → Environment variables (do not commit the URL). Alternative: **Email Extension** plugin with `emailext` in `post { failure }`.

## Definition of done

- [ ] `kubectl get pods -n monitoring` — prometheus, grafana, kube-state-metrics Running; node-exporter on each node
- [ ] Prometheus targets: app + kube-state-metrics + node-exporter **UP**
- [ ] Grafana dashboard **Capstone — App & Cluster** visible
- [ ] Test alert `CapstoneAppDown` once (scale to 0)
- [ ] Optional: `SLACK_WEBHOOK_URL` test on failed build

## Next: Sprint 6

See [sprint-6.md](sprint-6.md) and [e2e-testing.md](e2e-testing.md).
