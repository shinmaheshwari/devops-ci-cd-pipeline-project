# Sprint 1 Log

## Status: in progress

## Local verification

```bash
cd app
docker build -t app:local .
docker run -p 8080:8080 app:local
curl http://localhost:8080/health
```

Expected: `{"status": "ok", "uptime_seconds": ...}`

## AWS bootstrap (fill in as you complete each)

- [ ] AWS region chosen: `ap-south-1`
- [ ] ECR repo created: `devops-capstone-app` — URI: `<fill in after creation>`
- [ ] Jenkins EC2 launched — instance type: `t3.small` / `t3.medium`, SG restricted to my IP on 22/8080
- [ ] Key pair created and saved securely (not in repo)

## Jenkins setup

- [ ] Jenkins reachable at: `http://<EC2-public-ip>:8080`
- [ ] Plugins installed: Docker, Kubernetes, Pipeline, Git, AWS Credentials, Credentials Binding
- [ ] AWS credentials configured (prefer IAM instance profile over static keys)
- [ ] GitHub webhook or SCM poll configured
- [ ] First pipeline run: build image → push to ECR — build #: `<fill in>`

## Links

- Architecture doc: [architecture.md](architecture.md)
- ECR console: `<fill in>`
- Jenkins job: `<fill in>`

## Definition of done checklist

- [ ] Jenkins builds and pushes image to ECR
- [ ] Architecture doc complete
- [ ] kubeconfig access to EKS attempted (full cluster comes in Sprint 2)
