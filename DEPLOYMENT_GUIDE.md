# TCU CEAA - Docker & Kubernetes Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer / Ingress                  │
│                    (AWS ALB / GCP GLB / Azure AG)               │
└─────────────────────────────────────────────────────────────────┘
                    │                          │
        ┌───────────┴──────────┐    ┌─────────┴──────────┐
        │   Frontend (React)   │    │  Backend (Django)  │
        │   Nginx + Static     │    │  Gunicorn + API    │
        │   2-5 replicas       │    │  3-10 replicas     │
        └──────────────────────┘    └────────────────────┘
                                              │
                             ┌────────────────┼────────────────┐
                             │                │                │
                    ┌────────┴────────┐  ┌───┴────┐  ┌────────┴─────────┐
                    │ Celery Workers  │  │ Redis  │  │   PostgreSQL     │
                    │ ML/Vision Tasks │  │ Queue  │  │   (RDS/Cloud)    │
                    │ 2-8 replicas    │  └────────┘  └──────────────────┘
                    └─────────────────┘
                             │
                    ┌────────┴────────┐
                    │  AWS Services   │
                    │  - S3 (Media)   │
                    │  - Textract     │
                    │  - CloudFront   │
                    └─────────────────┘
```

## Components

### 1. Frontend (React + TypeScript)
- **Hosting**: Static hosting via Nginx in container
- **Alternatives**: AWS S3 + CloudFront, Vercel, Netlify
- **Resources**: 128-256MB RAM, 100-200m CPU
- **Scaling**: 2-5 replicas based on traffic

### 2. Backend API (Django + DRF)
- **Container**: Gunicorn with 4 workers, 2 threads
- **Resources**: 512MB-1GB RAM, 500m-1000m CPU
- **Scaling**: 3-10 replicas (HPA at 70% CPU)
- **Health**: `/health/` endpoint for liveness/readiness

### 3. Celery Workers (ML/Vision)
- **Tasks**: YOLOv8 detection, AWS Textract OCR, Liveness detection
- **Resources**: 1-2GB RAM, 1-2 CPU cores
- **Scaling**: 2-8 replicas (HPA at 75% CPU)
- **Queue**: Redis

### 4. Database (PostgreSQL)
- **Recommended**: Managed service (AWS RDS, GCP Cloud SQL, Azure Database)
- **K8s Option**: StatefulSet with persistent volume
- **Storage**: 20GB minimum, auto-scaling recommended

### 5. Cache/Queue (Redis)
- **Purpose**: Celery task queue, session cache
- **Resources**: 128-256MB RAM
- **Scaling**: Single instance (or Redis Sentinel for HA)

## Prerequisites

### Required Tools
```bash
# Docker
docker --version  # >= 20.10

# Kubernetes CLI
kubectl version   # >= 1.24

# Cloud CLI (choose one)
aws --version     # AWS
gcloud version    # GCP
az --version      # Azure
```

### Required Services
- Container Registry (ECR, GCR, ACR, or Docker Hub)
- Kubernetes Cluster (EKS, GKE, AKS)
- Managed PostgreSQL (RDS, Cloud SQL, Azure Database)
- S3 or compatible object storage
- AWS Textract API access

## Setup Instructions

### Step 1: Configure Environment Variables

1. **Update `k8s/01-secrets.yaml`:**
```yaml
# Generate Django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update with real values:
- POSTGRES_PASSWORD
- SECRET_KEY
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_STORAGE_BUCKET_NAME
```

2. **Update `k8s/01-secrets.yaml` ConfigMap:**
```yaml
- ALLOWED_HOSTS: "api.yourdomain.com,backend-service"
```

### Step 2: Create S3 Bucket

```bash
# AWS
aws s3 mb s3://tcu-ceaa-media --region us-east-1
aws s3api put-public-access-block \
    --bucket tcu-ceaa-media \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Configure CORS
aws s3api put-bucket-cors --bucket tcu-ceaa-media --cors-configuration file://s3-cors.json
```

### Step 3: Build and Push Docker Images

```bash
# Set your registry URL
export REGISTRY="123456789.dkr.ecr.us-east-1.amazonaws.com"  # AWS ECR
# OR
export REGISTRY="gcr.io/your-project-id"  # GCP GCR
# OR
export REGISTRY="yourusername"  # Docker Hub

# Login to registry
docker login $REGISTRY

# Build and push (Linux/Mac)
chmod +x scripts/build-images.sh
./scripts/build-images.sh v1.0.0

# Or manually build
docker build -f backend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-backend:v1.0.0 ./backend
docker build -f backend/Dockerfile.celery -t $REGISTRY/tcu-ceaa-celery:v1.0.0 ./backend
docker build -f frontend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-frontend:v1.0.0 ./frontend

docker push $REGISTRY/tcu-ceaa-backend:v1.0.0
docker push $REGISTRY/tcu-ceaa-celery:v1.0.0
docker push $REGISTRY/tcu-ceaa-frontend:v1.0.0
```

### Step 4: Update Kubernetes Manifests

Replace `YOUR_REGISTRY` in all k8s/*.yaml files:
```bash
# Linux/Mac
sed -i 's|YOUR_REGISTRY|'$REGISTRY'|g' k8s/*.yaml

# Windows (PowerShell)
Get-ChildItem k8s/*.yaml | ForEach-Object {
    (Get-Content $_) -replace 'YOUR_REGISTRY', $env:REGISTRY | Set-Content $_
}
```

### Step 5: Deploy to Kubernetes

```bash
# Connect to your cluster
kubectl config use-context your-cluster-context

# Deploy (Linux/Mac)
chmod +x scripts/deploy-k8s.sh
./scripts/deploy-k8s.sh

# Or deploy manually
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-secrets.yaml
kubectl apply -f k8s/02-postgres.yaml
kubectl apply -f k8s/03-redis.yaml
kubectl apply -f k8s/04-backend.yaml
kubectl apply -f k8s/05-celery-worker.yaml
kubectl apply -f k8s/06-frontend.yaml
kubectl apply -f k8s/07-ingress.yaml
```

### Step 6: Verify Deployment

```bash
# Check all resources
kubectl get all -n tcu-ceaa

# Check pods status
kubectl get pods -n tcu-ceaa

# Check logs
kubectl logs -f deployment/backend -n tcu-ceaa
kubectl logs -f deployment/celery-worker -n tcu-ceaa

# Get external IP
kubectl get ingress -n tcu-ceaa
kubectl get svc frontend-service -n tcu-ceaa
```

## Cloud Provider Specific Configurations

### AWS (EKS)

1. **Create EKS Cluster:**
```bash
eksctl create cluster \
  --name tcu-ceaa-cluster \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed
```

2. **Install AWS Load Balancer Controller:**
```bash
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=tcu-ceaa-cluster
```

3. **Use RDS PostgreSQL:**
```yaml
# In k8s/01-secrets.yaml
DATABASE_URL: "postgresql://admin:password@tcu-ceaa-db.xxxx.us-east-1.rds.amazonaws.com:5432/tcu_ceaa"
```

### GCP (GKE)

1. **Create GKE Cluster:**
```bash
gcloud container clusters create tcu-ceaa-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5
```

2. **Use Cloud SQL:**
```bash
gcloud sql instances create tcu-ceaa-db \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1
```

### Azure (AKS)

1. **Create AKS Cluster:**
```bash
az aks create \
  --resource-group tcu-ceaa-rg \
  --name tcu-ceaa-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 5
```

2. **Use Azure Database for PostgreSQL:**
```bash
az postgres server create \
  --resource-group tcu-ceaa-rg \
  --name tcu-ceaa-db \
  --location eastus \
  --sku-name B_Gen5_1 \
  --version 15
```

## Local Testing with Docker Compose

```bash
# Copy environment file
cp .env.example .env

# Update .env with your credentials

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## Monitoring & Logging

### Install Monitoring Stack

```bash
# Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Get Grafana password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

### View Logs

```bash
# Install Elasticsearch + Kibana (optional)
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n logging --create-namespace
helm install kibana elastic/kibana -n logging
```

## Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n tcu-ceaa

# Scale celery workers
kubectl scale deployment celery-worker --replicas=4 -n tcu-ceaa
```

### Auto-scaling (already configured via HPA)
- Backend: 3-10 replicas (70% CPU threshold)
- Celery: 2-8 replicas (75% CPU threshold)
- Frontend: 2-5 replicas (70% CPU threshold)

## Backup & Disaster Recovery

### Database Backups
```bash
# Manual backup
kubectl exec -n tcu-ceaa postgres-0 -- pg_dump -U postgres tcu_ceaa > backup.sql

# Restore
kubectl exec -i -n tcu-ceaa postgres-0 -- psql -U postgres tcu_ceaa < backup.sql
```

### Automated Backups
Use managed database services for automated backups:
- AWS RDS: Automated snapshots
- GCP Cloud SQL: Automated backups
- Azure Database: Automated backups

## Security Best Practices

1. **Use Managed Databases** instead of in-cluster PostgreSQL
2. **Enable Network Policies** to restrict pod-to-pod communication
3. **Use Secrets Management**: AWS Secrets Manager, GCP Secret Manager, Azure Key Vault
4. **Enable Pod Security Policies**
5. **Regular Security Scans**: Trivy, Clair for container scanning
6. **TLS Everywhere**: Use cert-manager for automatic SSL certificates
7. **RBAC**: Implement proper role-based access control

## Cost Optimization

1. **Use Spot/Preemptible Instances** for Celery workers
2. **Right-size Resources**: Monitor and adjust CPU/memory requests
3. **Use S3/CloudFront** for static assets instead of serving from pods
4. **Enable Cluster Autoscaler** to scale nodes based on demand
5. **Use Reserved Instances** for production databases

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n tcu-ceaa
kubectl logs <pod-name> -n tcu-ceaa
```

### Database connection issues
```bash
# Test from backend pod
kubectl exec -it deployment/backend -n tcu-ceaa -- python manage.py dbshell
```

### Celery workers not processing tasks
```bash
# Check Celery logs
kubectl logs deployment/celery-worker -n tcu-ceaa

# Inspect Celery
kubectl exec -it deployment/celery-worker -n tcu-ceaa -- celery -A backend_project inspect active
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push images
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          ./scripts/build-images.sh ${{ github.sha }}
      - name: Deploy to k8s
        run: |
          kubectl apply -f k8s/
```

## Support & Contact

For issues and questions, please refer to the project documentation or create an issue in the repository.
