# Sprint 1 Log

## Status: complete

## Local verification

```bash
cd app
docker build -t app:local .
docker run -p 8080:8080 app:local
curl http://localhost:8080/health
```

Result: `{"status": "ok", "uptime_seconds": ...}` — confirmed working after fixing a
Docker file-permission bug (see Lessons Learned).

## AWS bootstrap

- [x] AWS region chosen: `ap-south-1`
- [x] ECR repo created: `devops-capstone-app` — URI: `562904760755.dkr.ecr.ap-south-1.amazonaws.com/devops-capstone-app`
- [x] Jenkins EC2 launched — instance type: `t3.medium`, instance ID `i-0adf876798c6081fe`, SG `sg-035635846fd281b71` restricted to my IP on 22/8080
- [x] Key pair created and saved securely (not in repo) — `jenkins-capstone-key`
- [x] IAM role `jenkins-capstone-role` + instance profile `jenkins-capstone-profile`, with `AmazonEC2ContainerRegistryFullAccess` and `AmazonSSMManagedInstanceCore` attached

## Jenkins setup

- [x] Jenkins reachable at `http://localhost:8080` via SSM port-forward tunnel (see Lessons Learned — direct access is blocked on my network)
- [x] Plugins installed: Docker Pipeline, Amazon ECR, Pipeline: AWS Steps, Git
- [x] AWS credentials configured via IAM instance profile — verified with `aws sts get-caller-identity` as the `jenkins` user, confirmed no static keys needed
- [x] Pipeline job `capstone-build` created, pointed at `jenkins/Jenkinsfile` via Pipeline script from SCM
- [x] First pipeline run: build image → push to ECR — successful after two fixes (see Lessons Learned)

## Links

- Architecture doc: [architecture.md](architecture.md)
- ECR repo: `562904760755.dkr.ecr.ap-south-1.amazonaws.com/devops-capstone-app`
- Jenkins job: `capstone-build` (Pipeline script from SCM, `jenkins/Jenkinsfile`)
- Instance: `i-0adf876798c6081fe` (ap-south-1)

## Lessons learned / troubleshooting notes

These are worth keeping for the final documentation pass (Sprint 6) — they show real
infra problem-solving, not just a clean happy-path setup.

1. **Docker permission error (`PermissionError: [Errno 13]` on `/app/app.py`)** — the
   Dockerfile's `COPY . .` ran as root, but the runtime stage switches to a non-root
   `appuser` for security. Fixed by adding `--chown=appuser:appuser` to both `COPY`
   instructions so the app files are readable by the user that actually runs gunicorn.

2. **Corporate network (Zscaler) blocks raw SSH and non-standard HTTP ports** — direct
   `ssh` to the EC2 instance and direct `curl`/browser access to port 8080 both failed
   with "connection reset by peer" even though the security group and IP were correct.
   Diagnosed by comparing a successful raw TCP `nc` connection against a failing SSH
   handshake, then confirming Zscaler agents were running locally. Worked around by:
   - Using **AWS Systems Manager (SSM) Session Manager** instead of SSH for shell
     access (tunnels over HTTPS, which Zscaler doesn't intercept) — required adding
     `AmazonSSMManagedInstanceCore` to the instance's IAM role.
   - Using **SSM port forwarding** (`aws ssm start-session ... AWS-StartPortForwardingSession`)
     to reach the Jenkins UI at `localhost:8080` instead of the EC2 public IP directly.

3. **EC2 key pair mistake** — the original `create-key-pair` command's output redirect
   failed silently, so the `.pem` file was empty/missing even though AWS had already
   registered the key. Since AWS only exposes a private key once at creation, the fix
   was to delete and recreate the key pair, then terminate and relaunch the EC2
   instance with the new key (an existing running instance can't be "re-keyed").

4. **Jenkins apt repo GPG key was outdated** — the widely-documented
   `jenkins.io-2023.key` expired; Jenkins rotated signing keys for LTS starting
   January 2026. Fixed by using `jenkins.io-2026.key` instead. Separately, Ubuntu
   22.04's `apt-key`-based `signed-by` verification had a compatibility quirk with
   the dearmored keyring file even though `gpgv` independently verified the signature
   as valid — worked around by placing the key in `/etc/apt/trusted.gpg.d/` instead
   of using `signed-by` in the sources list.

5. **Jenkins 2.568.2 requires Java 21, but only Java 17 was installed** — Jenkins'
   own startup log gave a clear, direct error for this one (`Supported Java versions
   are: [21, 25]`). Fixed with `apt install openjdk-21-jre`; `update-alternatives`
   picked it up automatically.

6. **Missing `python3-venv` on the Jenkins host** — the pipeline's Test stage failed
   because the base install command (Step 6) didn't include Python packaging tools.
   Fixed with `apt install python3-venv python3-pip`. Worth adding to the base
   instance setup for any future EC2 relaunch.

## Definition of done checklist

- [x] Jenkins builds and pushes image to ECR
- [x] Architecture doc complete
- [x] kubeconfig access to EKS attempted (full cluster comes in Sprint 2 — N/A yet,
      no EKS cluster exists until Terraform creates one)

