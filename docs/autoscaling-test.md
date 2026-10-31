# Autoscaling test (HPA)

Goal: prove that the Horizontal Pod Autoscaler scales the app under real load, and scales it back down when the load stops.

## Setup

| Item | Value |
|---|---|
| HPA | [`kubernetes/hpa.yaml`](../kubernetes/hpa.yaml): min 2, max 5 replicas, target 70% average CPU |
| Pod resources | [`kubernetes/deployment.yaml`](../kubernetes/deployment.yaml): CPU request `100m`, limit `250m` (the 70% target is measured against the 100m request) |
| Metrics | metrics-server `v0.7.2`, installed by the Jenkins Deploy stage |
| Load | [`kubernetes/tests/load-generator.yaml`](../kubernetes/tests/load-generator.yaml): a BusyBox pod running 8 parallel request loops against the `capstone-app` Service inside the cluster |
| Cluster | 2 × t3.medium worker nodes in two private subnets (two availability zones) |

## Steps

1. Baseline: `kubectl get hpa,deploy -n capstone-app`
2. Reachability check from inside the cluster:
   `kubectl run curltest --rm -it --restart=Never --image=busybox:1.36 -n capstone-app -- wget -qO- http://capstone-app/health`
3. Start the load: `kubectl apply -f kubernetes/tests/load-generator.yaml`
4. Watch the autoscaler: `kubectl get hpa -n capstone-app -w`
5. Add a second generator to push to the maximum:
   `sed 's/name: load-generator/name: load-generator-2/' kubernetes/tests/load-generator.yaml | kubectl apply -f -`
6. Inspect the pods: `kubectl get pods -n capstone-app -o wide` and `kubectl top pods -n capstone-app`
7. Stop the load: `kubectl delete pod load-generator load-generator-2 -n capstone-app`
8. Watch the scale-down: `kubectl get hpa -n capstone-app -w`

## Results

| Phase | CPU (of target) | Replicas | Notes |
|---|---|---|---|
| Baseline | 1% / 70% | 2 | Idle |
| One load generator | 24% → 97% → **113%** | 2 → 3 → 4 | Scaled to 4 in about **2 minutes**; CPU then settled at 63–64%, below target, so the HPA held at 4 |
| Two load generators | above 70% | **5** (maximum) | Each app pod at 96–99m CPU (about its 100m request) |
| Load stopped | drops within a minute | 5 → **2** | After the HPA's ~5-minute scale-down stabilisation window |

Observations:

- **The HPA behaved as designed.** It added pods until average CPU fell back under the 70% target, then stopped adding; with more load it went up to the configured maximum of 5.
- **Pods were spread across both worker nodes**, which sit in different private subnets (`10.0.10.x` and `10.0.11.x`) and therefore different availability zones.
- **No pods were Pending.** The two t3.medium nodes had capacity for all 5 replicas, so node autoscaling was not needed at this scale.
- **Scale-down is deliberately slower than scale-up.** The ~5-minute stabilisation window stops the HPA removing pods during short dips in traffic.
- The load generators ran at their own 500m CPU limit (`499m`), which is expected: they produce as much traffic as their limit allows.

## Evidence

| Screenshot | Shows |
|---|---|
| ![](screenshots/sprint7-hpa-before.png) | Baseline: 2 replicas, CPU 1% of target |
| ![](screenshots/sprint7-hpa-scaling-up.png) | CPU rising to 113% and the HPA scaling 2 → 3 → 4 |
| ![](screenshots/sprint7-hpa-pods-scaled.png) | 5 replicas running across both nodes, with per-pod CPU |
| ![](screenshots/sprint7-grafana-load-test.png) | Request rate and CPU spike in Grafana during the test |
| ![](screenshots/sprint7-hpa-scaled-down.png) | Back to 2 replicas after the load stopped |

## Limitations and next steps

- **Pod autoscaling only.** The node group has a fixed size. With more load or larger pods, extra replicas would stay Pending until a node is added. Next step: Cluster Autoscaler or Karpenter.
- **CPU is the only scaling signal.** Request rate or latency (from Prometheus, through a custom-metrics adapter) would track user experience more directly.
- **Synthetic load.** The test hits the lightweight `/health` endpoint from inside the cluster; a production test would replay realistic traffic through the load balancer.
