# Monitoring — Sprint 5

## Status: implemented — verify targets/alerts after Jenkins run (see [e2e-testing.md](e2e-testing.md))

## What gets deployed

| Component | Namespace | Purpose |
|---|---|---|
| Prometheus | `monitoring` | Scrapes pods with `prometheus.io/*` annotations (capstone-app `/metrics`) |
| Grafana | `monitoring` | LoadBalancer UI, Prometheus datasource pre-provisioned |
| Alert rules | Prometheus config | `CapstoneAppDown`, high request rate (demo thresholds) |

The Jenkins **Monitoring** stage runs after the post-deploy smoke test and applies `monitoring/*.yaml`.

## Access Grafana

```bash
kubectl get svc grafana -n monitoring
# open http://<EXTERNAL-IP>/  — login admin / capstone-dev (dev-only password)
```

Or port-forward:

```bash
kubectl port-forward svc/grafana -n monitoring 3000:80
# http://localhost:3000
```

## Verify Prometheus targets

```bash
kubectl port-forward svc/prometheus -n monitoring 9090:9090
# http://localhost:9090/targets — capstone-app pods should be UP
```

## Jenkins failure notifications

Pipeline `post { failure { ... } }` logs a reminder to check Grafana/Prometheus. For production, add Email Extension or Slack webhook via Jenkins Credentials (not committed).

## Definition of done

- [ ] `kubectl get pods -n monitoring` — prometheus and grafana Running
- [ ] Prometheus targets show capstone-app pods UP
- [ ] Grafana loads with Prometheus datasource working
- [ ] Test alert: scale deployment to 0 or break `/metrics`, confirm alert in Prometheus UI
- [ ] Jenkins failure block documented / optional webhook configured

## Next: Sprint 6

End-to-end test doc, cost section, demo script, full trigger automation.
