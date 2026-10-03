# Jenkins — SCM triggers

The capstone expects builds when code changes. This project uses **Pipeline from SCM** plus one or both of the following.

## 1. Poll SCM (in Jenkinsfile)

The Jenkinsfile includes:

```groovy
triggers {
    pollSCM('H/15 * * * *')
}
```

Jenkins checks the repository every ~15 minutes; if the configured branch has new commits, it starts a build. No inbound firewall rules required on Jenkins.

**Tradeoff:** Up to 15 minutes delay vs instant webhooks.

## 2. GitHub webhook (recommended for demos)

1. Jenkins job → **Build Triggers** → enable **GitHub hook trigger for GITScm polling** (if GitHub plugin installed).
2. GitHub repo → **Settings → Webhooks** → Payload URL `http(s)://<jenkins>/github-webhook/`, event **Push**.
3. If Jenkins is only reachable via SSM port-forward, webhooks need a tunnel or use poll-only.

## Job configuration checklist

| Setting | Value |
|---------|--------|
| Definition | Pipeline script from SCM |
| SCM | Git → your repo URL |
| Branch Specifier | `*/main` (update when testing feature branches) |
| Script Path | `jenkins/Jenkinsfile` |

## Stacked PR testing

While reviewing PR #3 then #4:

- Temporarily set Branch Specifier to `*/feat/sprint-5-monitoring` or `*/feat/sprint-6-finalization`
- After merge, **reset to `*/main`**

See [pipeline.md](pipeline.md) — stale branch specifier caused false “green” builds in Sprint 4.
