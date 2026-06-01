# devops-ci-cd-pipeline-project
End to End DevOps CI/CD pipeline using Jenkins, Terraform, Ansible and EKS

## Project Structure

```
devops-cicd-pipeline-project/
│
├── app/                  # Application code
│   └── (your web app)
│
├── docker/
│   └── Dockerfile
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── backend.tf
│
├── ansible/
│   ├── playbook.yml
│   └── inventory.ini
│
├── jenkins/
│   └── Jenkinsfile
│
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
│
├── monitoring/
│   ├── prometheus.yaml
│   └── grafana-dashboard.json
│
└── README.md
```
