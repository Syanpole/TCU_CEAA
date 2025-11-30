# 🚀 TCU CEAA - GCP + AWS Hybrid Cloud Deployment Guide

## 📋 Architecture Overview

This guide covers deploying TCU CEAA on **Google Cloud Platform (GCP)** while leveraging **AWS services** for specialized AI/ML capabilities:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform (GCP)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │  Cloud Load  │────▶│  GKE Cluster │────▶│  Cloud SQL   │        │
│  │   Balancer   │     │  (Kubernetes)│     │ (PostgreSQL) │        │
│  └──────────────┘     └──────────────┘     └──────────────┘        │
│                              │                                       │
│  ┌──────────────┐     ┌─────┴──────┐      ┌──────────────┐        │
│  │ Artifact     │     │  Cloud Run │      │  Memorystore │        │
│  │ Registry     │     │  (Optional)│      │   (Redis)    │        │
│  └──────────────┘     └────────────┘      └──────────────┘        │
│                                                                       │
└───────────────────────────────────┬───────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
┌───────────────────▼──────┐  ┌────▼─────┐  ┌──────▼──────────┐
│    AWS S3 Storage         │  │   AWS    │  │      AWS        │
│  - Document Storage       │  │Textract  │  │  Rekognition    │
│  - Birth Certificates     │  │   OCR    │  │  Face Match     │
│  - School IDs             │  │  Service │  │  Face Liveness  │
│  - Grade Documents        │  └──────────┘  └─────────────────┘
└───────────────────────────┘
```

### Why This Hybrid Architecture?

1. **GCP for Infrastructure**:
   - Cost-effective Kubernetes hosting (GKE)
   - Excellent Cloud SQL for PostgreSQL
   - Fast Cloud Build CI/CD
   - Superior networking performance

2. **AWS for AI Services**:
   - **S3**: Industry-leading object storage with 99.999999999% durability
   - **Textract**: Best-in-class document OCR (birth certificates, IDs, grades)
   - **Rekognition**: Advanced face verification and liveness detection
   - No equivalent GCP services with the same accuracy

---

## 📅 Deployment Timeline

### Day 1 (4-5 hours): GCP Infrastructure Setup
- Create GCP project
- Set up GKE cluster
- Configure Cloud SQL (PostgreSQL)
- Set up Artifact Registry
- Configure IAM and service accounts

### Day 2 (3-4 hours): AWS Services Integration
- Create S3 bucket
- Enable Textract API
- Enable Rekognition API
- Configure IAM policies
- Set up cross-cloud credentials

### Day 3 (4-5 hours): Application Deployment
- Build and push Docker images
- Deploy to GKE
- Configure secrets and ConfigMaps
- Set up Cloud Load Balancer
- Configure DNS

### Day 4 (2-3 hours): Testing & Optimization
- Run integration tests
- Verify AWS service connectivity
- Performance tuning
- Security hardening

---

## 🔧 Prerequisites

### Required Accounts
- [ ] Google Cloud Platform account with billing enabled
- [ ] AWS account with billing enabled
- [ ] Domain name (optional, for production)

### Required Tools
```powershell
# Install Google Cloud SDK
# Download from: https://cloud.google.com/sdk/docs/install
gcloud --version

# Install kubectl
gcloud components install kubectl
kubectl version --client

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop
docker --version

# Install AWS CLI (for S3, Textract, Rekognition)
# Download from: https://aws.amazon.com/cli/
aws --version

# Verify installations
gcloud version
kubectl version --client
docker --version
aws --version
```

---

## 📦 Part 1: GCP Infrastructure Setup

### Step 1.1: Create GCP Project (15 minutes)

#### 1.1.1 Create New Project
```powershell
# Login to GCP
gcloud auth login

# Create project
gcloud projects create tcu-ceaa-staging --name="TCU CEAA Staging"

# Set as default project
gcloud config set project tcu-ceaa-staging

# Verify
gcloud config get-value project
# Expected: tcu-ceaa-staging
```

#### 1.1.2 Enable Required APIs
```powershell
# Enable all required GCP APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com

# Verify enabled services
gcloud services list --enabled
```

#### 1.1.3 Set Up Billing
```powershell
# List billing accounts
gcloud billing accounts list

# Link billing account to project (replace BILLING_ACCOUNT_ID)
gcloud billing projects link tcu-ceaa-staging `
  --billing-account=BILLING_ACCOUNT_ID

# Verify billing is enabled
gcloud billing projects describe tcu-ceaa-staging
```

---

### Step 1.2: Create GKE Cluster (30 minutes)

#### 1.2.1 Configure Cluster Settings
```powershell
# Set region (choose closest to your users)
# Options: us-central1, us-east1, us-west1, europe-west1, asia-southeast1
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Create GKE cluster (Standard tier for staging)
gcloud container clusters create tcu-ceaa-cluster `
  --region=us-central1 `
  --num-nodes=2 `
  --machine-type=e2-standard-2 `
  --disk-size=50 `
  --disk-type=pd-standard `
  --enable-autoscaling `
  --min-nodes=2 `
  --max-nodes=5 `
  --enable-autorepair `
  --enable-autoupgrade `
  --enable-stackdriver-kubernetes `
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing `
  --workload-pool=tcu-ceaa-staging.svc.id.goog

# This takes 10-15 minutes...
```

#### 1.2.2 Connect to Cluster
```powershell
# Get cluster credentials
gcloud container clusters get-credentials tcu-ceaa-cluster `
  --region=us-central1

# Verify connection
kubectl cluster-info
kubectl get nodes

# Expected output:
# NAME                                           STATUS   ROLES    AGE
# gke-tcu-ceaa-cluster-default-pool-xxxxx-xxxx   Ready    <none>   5m
# gke-tcu-ceaa-cluster-default-pool-xxxxx-xxxx   Ready    <none>   5m
```

---

### Step 1.3: Set Up Cloud SQL (PostgreSQL) (20 minutes)

#### 1.3.1 Create PostgreSQL Instance
```powershell
# Create Cloud SQL instance
gcloud sql instances create tcu-ceaa-postgres `
  --database-version=POSTGRES_14 `
  --tier=db-f1-micro `
  --region=us-central1 `
  --storage-type=SSD `
  --storage-size=10GB `
  --storage-auto-increase `
  --backup-start-time=03:00 `
  --maintenance-window-day=SUN `
  --maintenance-window-hour=04 `
  --enable-bin-log

# This takes 5-10 minutes...

# Get instance connection name
gcloud sql instances describe tcu-ceaa-postgres `
  --format="value(connectionName)"
# Save this value: PROJECT:REGION:INSTANCE_NAME
# Example: tcu-ceaa-staging:us-central1:tcu-ceaa-postgres
```

#### 1.3.2 Set Root Password
```powershell
# Set postgres user password
gcloud sql users set-password postgres `
  --instance=tcu-ceaa-postgres `
  --password=YOUR_SECURE_PASSWORD_HERE

# Note: Replace YOUR_SECURE_PASSWORD_HERE with a strong password
# Save this password - you'll need it later!
```

#### 1.3.3 Create Application Database
```powershell
# Create database
gcloud sql databases create tcu_ceaa_db `
  --instance=tcu-ceaa-postgres

# Verify database created
gcloud sql databases list --instance=tcu-ceaa-postgres
```

---

### Step 1.4: Set Up Memorystore (Redis) (15 minutes)

#### 1.4.1 Create Redis Instance
```powershell
# Create Memorystore Redis instance
gcloud redis instances create tcu-ceaa-redis `
  --size=1 `
  --region=us-central1 `
  --redis-version=redis_6_x `
  --tier=basic

# This takes 5-10 minutes...

# Get Redis host and port
gcloud redis instances describe tcu-ceaa-redis `
  --region=us-central1 `
  --format="value(host,port)"
# Save these values for later
```

---

### Step 1.5: Set Up Artifact Registry (10 minutes)

#### 1.5.1 Create Docker Repository
```powershell
# Create Artifact Registry repository
gcloud artifacts repositories create tcu-ceaa-repo `
  --repository-format=docker `
  --location=us-central1 `
  --description="TCU CEAA Docker images"

# Configure Docker to use gcloud credentials
gcloud auth configure-docker us-central1-docker.pkg.dev

# Verify repository
gcloud artifacts repositories list
```

---

### Step 1.6: Set Up GCP Service Account (15 minutes)

#### 1.6.1 Create Service Account for Application
```powershell
# Create service account
gcloud iam service-accounts create tcu-ceaa-app `
  --display-name="TCU CEAA Application" `
  --description="Service account for TCU CEAA application"

# Get service account email
$SA_EMAIL = gcloud iam service-accounts list `
  --filter="displayName:TCU CEAA Application" `
  --format="value(email)"

Write-Output "Service Account Email: $SA_EMAIL"
```

#### 1.6.2 Grant Required Permissions
```powershell
# Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding tcu-ceaa-staging `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/cloudsql.client"

# Grant Storage Admin role (for logs, if needed)
gcloud projects add-iam-policy-binding tcu-ceaa-staging `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/storage.admin"

# Grant Artifact Registry Reader role
gcloud projects add-iam-policy-binding tcu-ceaa-staging `
  --member="serviceAccount:$SA_EMAIL" `
  --role="roles/artifactregistry.reader"
```

#### 1.6.3 Create and Download Service Account Key
```powershell
# Create key file
gcloud iam service-accounts keys create gcp-service-account-key.json `
  --iam-account=$SA_EMAIL

# IMPORTANT: Keep this file secure!
# Move it to a safe location
Move-Item gcp-service-account-key.json ~\.gcp\tcu-ceaa-key.json

Write-Output "Service account key saved to: $HOME\.gcp\tcu-ceaa-key.json"
```

---

## 🔗 Part 2: AWS Services Integration

### Step 2.1: Configure AWS Account (10 minutes)

#### 2.1.1 Set Up AWS CLI
```powershell
# Configure AWS credentials
aws configure

# Enter your AWS credentials:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
# Default output format: json

# Verify connection
aws sts get-caller-identity
```

#### 2.1.2 Set AWS Region
```powershell
# Set region for all AWS services
$env:AWS_DEFAULT_REGION = "us-east-1"

# Verify region
aws configure get region
# Expected: us-east-1
```

---

### Step 2.2: Create S3 Bucket (15 minutes)

#### 2.2.1 Create Staging Bucket
```powershell
# Create S3 bucket
aws s3 mb s3://tcu-ceaa-staging-documents --region us-east-1

# Enable versioning (recommended for production)
aws s3api put-bucket-versioning `
  --bucket tcu-ceaa-staging-documents `
  --versioning-configuration Status=Enabled

# Verify bucket created
aws s3 ls | Select-String "tcu-ceaa"
```

#### 2.2.2 Configure Bucket CORS
```powershell
# Create CORS configuration file
@"
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
"@ | Out-File -Encoding utf8 cors-config.json

# Apply CORS configuration
aws s3api put-bucket-cors `
  --bucket tcu-ceaa-staging-documents `
  --cors-configuration file://cors-config.json

# Verify CORS
aws s3api get-bucket-cors --bucket tcu-ceaa-staging-documents
```

#### 2.2.3 Set Bucket Lifecycle Policy (Optional)
```powershell
# Create lifecycle policy for cost optimization
@"
{
  "Rules": [
    {
      "Id": "MoveToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 180,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
"@ | Out-File -Encoding utf8 lifecycle-policy.json

# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration `
  --bucket tcu-ceaa-staging-documents `
  --lifecycle-configuration file://lifecycle-policy.json
```

---

### Step 2.3: Enable AWS Textract (10 minutes)

#### 2.3.1 Verify Textract Access
```powershell
# Test Textract API access
aws textract help

# Check service quota
aws service-quotas list-service-quotas `
  --service-code textract `
  --query 'Quotas[?QuotaName==`Max concurrent jobs`]'
```

#### 2.3.2 Create IAM Policy for Textract
```powershell
# Create Textract policy file
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument",
        "textract:AnalyzeID",
        "textract:StartDocumentAnalysis",
        "textract:GetDocumentAnalysis"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::tcu-ceaa-staging-documents/*"
    }
  ]
}
"@ | Out-File -Encoding utf8 textract-policy.json

# Create IAM policy
aws iam create-policy `
  --policy-name TCU-CEAA-Textract-Policy `
  --policy-document file://textract-policy.json
```

---

### Step 2.4: Enable AWS Rekognition (10 minutes)

#### 2.4.1 Verify Rekognition Access
```powershell
# Test Rekognition API access
aws rekognition help

# Check service availability
aws rekognition describe-projects --max-results 1
```

#### 2.4.2 Create IAM Policy for Rekognition
```powershell
# Create Rekognition policy file
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:CompareFaces",
        "rekognition:DetectFaces",
        "rekognition:CreateFaceLivenessSession",
        "rekognition:GetFaceLivenessSessionResults",
        "rekognition:DetectModerationLabels"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::tcu-ceaa-staging-documents/*"
    }
  ]
}
"@ | Out-File -Encoding utf8 rekognition-policy.json

# Create IAM policy
aws iam create-policy `
  --policy-name TCU-CEAA-Rekognition-Policy `
  --policy-document file://rekognition-policy.json
```

---

### Step 2.5: Create AWS IAM User for Application (15 minutes)

#### 2.5.1 Create IAM User
```powershell
# Create IAM user
aws iam create-user --user-name tcu-ceaa-app

# Get account ID
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text

# Attach policies to user
aws iam attach-user-policy `
  --user-name tcu-ceaa-app `
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/TCU-CEAA-Textract-Policy"

aws iam attach-user-policy `
  --user-name tcu-ceaa-app `
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/TCU-CEAA-Rekognition-Policy"

# Attach S3 full access
aws iam attach-user-policy `
  --user-name tcu-ceaa-app `
  --policy-arn "arn:aws:iam::aws:policy/AmazonS3FullAccess"
```

#### 2.5.2 Create Access Keys
```powershell
# Create access key
$AWS_KEYS = aws iam create-access-key --user-name tcu-ceaa-app | ConvertFrom-Json

# Save keys securely
$AWS_ACCESS_KEY_ID = $AWS_KEYS.AccessKey.AccessKeyId
$AWS_SECRET_ACCESS_KEY = $AWS_KEYS.AccessKey.SecretAccessKey

Write-Output "=== IMPORTANT: SAVE THESE AWS CREDENTIALS ==="
Write-Output "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
Write-Output "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"
Write-Output "=============================================="

# Save to secure file
@"
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME=tcu-ceaa-staging-documents
AWS_S3_REGION_NAME=us-east-1
"@ | Out-File -Encoding utf8 ~\.aws\tcu-ceaa-credentials.txt

Write-Output "Credentials saved to: $HOME\.aws\tcu-ceaa-credentials.txt"
```

---

## 🚀 Part 3: Application Deployment

### Step 3.1: Prepare Environment Configuration (15 minutes)

#### 3.1.1 Create Kubernetes Namespace
```powershell
# Navigate to project directory
cd d:\Python\TCU_CEAA

# Create namespace
kubectl create namespace tcu-ceaa-staging

# Set default namespace
kubectl config set-context --current --namespace=tcu-ceaa-staging

# Verify
kubectl get namespaces
```

#### 3.1.2 Create Kubernetes Secrets
```powershell
# Generate Django secret key
$DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Get Cloud SQL connection string
$SQL_CONNECTION_NAME = gcloud sql instances describe tcu-ceaa-postgres --format="value(connectionName)"

# Create secrets YAML file
@"
apiVersion: v1
kind: Secret
metadata:
  name: tcu-ceaa-secrets
  namespace: tcu-ceaa-staging
type: Opaque
stringData:
  # Django
  SECRET_KEY: "$DJANGO_SECRET_KEY"
  DEBUG: "False"
  
  # Database (Cloud SQL)
  DB_NAME: "tcu_ceaa_db"
  DB_USER: "postgres"
  DB_PASSWORD: "YOUR_POSTGRES_PASSWORD"
  DB_HOST: "/cloudsql/$SQL_CONNECTION_NAME"
  DB_PORT: "5432"
  
  # Redis (Memorystore)
  REDIS_HOST: "YOUR_REDIS_HOST"
  REDIS_PORT: "6379"
  REDIS_PASSWORD: ""
  
  # AWS Credentials
  AWS_ACCESS_KEY_ID: "$AWS_ACCESS_KEY_ID"
  AWS_SECRET_ACCESS_KEY: "$AWS_SECRET_ACCESS_KEY"
  AWS_STORAGE_BUCKET_NAME: "tcu-ceaa-staging-documents"
  AWS_S3_REGION_NAME: "us-east-1"
  
  # AWS Services
  AWS_TEXTRACT_ENABLED: "True"
  AWS_REKOGNITION_ENABLED: "True"
  
  # Application URLs
  ALLOWED_HOSTS: "*.run.app,*.cloudflare.com,localhost"
  CORS_ALLOWED_ORIGINS: "https://yourdomain.com"
"@ | Out-File -Encoding utf8 k8s-secrets.yaml

# Apply secrets
kubectl apply -f k8s-secrets.yaml

# Verify secrets created
kubectl get secrets -n tcu-ceaa-staging
```

---

### Step 3.2: Build Docker Images (30 minutes)

#### 3.2.1 Build Backend Image
```powershell
# Set variables
$PROJECT_ID = "tcu-ceaa-staging"
$REGION = "us-central1"
$REPO = "tcu-ceaa-repo"

# Build backend image
docker build `
  -f backend/Dockerfile.prod `
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:latest `
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:v1.0.0 `
  ./backend

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:latest
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/backend:v1.0.0
```

#### 3.2.2 Build Frontend Image
```powershell
# Build frontend image with API URL
$BACKEND_URL = "https://tcu-ceaa-backend-xxxxx-uc.a.run.app"  # Update after backend deployment

docker build `
  -f frontend/Dockerfile.prod `
  --build-arg REACT_APP_API_URL=$BACKEND_URL `
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:latest `
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:v1.0.0 `
  ./frontend

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:latest
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/frontend:v1.0.0
```

#### 3.2.3 Verify Images
```powershell
# List images in registry
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}

# Expected output:
# IMAGE                                                              TAG
# us-central1-docker.pkg.dev/tcu-ceaa-staging/tcu-ceaa-repo/backend  latest, v1.0.0
# us-central1-docker.pkg.dev/tcu-ceaa-staging/tcu-ceaa-repo/frontend latest, v1.0.0
```

---

### Step 3.3: Deploy to GKE (45 minutes)

#### 3.3.1 Create Backend Deployment
```powershell
# Create backend deployment YAML
@"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: tcu-ceaa-staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      serviceAccountName: tcu-ceaa-app
      containers:
      - name: backend
        image: us-central1-docker.pkg.dev/tcu-ceaa-staging/tcu-ceaa-repo/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: tcu-ceaa-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      
      # Cloud SQL Proxy sidecar
      - name: cloud-sql-proxy
        image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.8.0
        args:
          - "--structured-logs"
          - "--port=5432"
          - "$SQL_CONNECTION_NAME"
        securityContext:
          runAsNonRoot: true
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: tcu-ceaa-staging
spec:
  type: LoadBalancer
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8000
"@ | Out-File -Encoding utf8 k8s-backend-deployment.yaml

# Apply backend deployment
kubectl apply -f k8s-backend-deployment.yaml

# Wait for deployment
kubectl rollout status deployment/backend -n tcu-ceaa-staging

# Get backend external IP
kubectl get service backend-service -n tcu-ceaa-staging
```

#### 3.3.2 Create Celery Worker Deployment
```powershell
# Create Celery worker deployment YAML
@"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
  namespace: tcu-ceaa-staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      serviceAccountName: tcu-ceaa-app
      containers:
      - name: celery-worker
        image: us-central1-docker.pkg.dev/tcu-ceaa-staging/tcu-ceaa-repo/backend:latest
        command: ["celery"]
        args: ["-A", "backend_project", "worker", "-l", "info", "--concurrency=4"]
        envFrom:
        - secretRef:
            name: tcu-ceaa-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
      
      # Cloud SQL Proxy sidecar
      - name: cloud-sql-proxy
        image: gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.8.0
        args:
          - "--structured-logs"
          - "--port=5432"
          - "$SQL_CONNECTION_NAME"
        securityContext:
          runAsNonRoot: true
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
"@ | Out-File -Encoding utf8 k8s-celery-deployment.yaml

# Apply Celery deployment
kubectl apply -f k8s-celery-deployment.yaml

# Verify deployment
kubectl rollout status deployment/celery-worker -n tcu-ceaa-staging
```

#### 3.3.3 Create Frontend Deployment
```powershell
# Create frontend deployment YAML
@"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: tcu-ceaa-staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: us-central1-docker.pkg.dev/tcu-ceaa-staging/tcu-ceaa-repo/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: tcu-ceaa-staging
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
"@ | Out-File -Encoding utf8 k8s-frontend-deployment.yaml

# Apply frontend deployment
kubectl apply -f k8s-frontend-deployment.yaml

# Wait for deployment
kubectl rollout status deployment/frontend -n tcu-ceaa-staging

# Get frontend external IP
kubectl get service frontend-service -n tcu-ceaa-staging
```

---

### Step 3.4: Run Database Migrations (10 minutes)

```powershell
# Get backend pod name
$BACKEND_POD = kubectl get pods -n tcu-ceaa-staging -l app=backend -o jsonpath='{.items[0].metadata.name}'

# Run migrations
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- python manage.py migrate

# Create superuser (optional)
kubectl exec -it -n tcu-ceaa-staging $BACKEND_POD -- python manage.py createsuperuser

# Collect static files (if needed)
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- python manage.py collectstatic --noinput
```

---

### Step 3.5: Configure Cloud Build (Optional - CI/CD) (20 minutes)

#### 3.5.1 Update cloudbuild.yaml
```powershell
# Update cloudbuild.yaml with GCP-specific settings
# (File already exists, just verify substitutions)

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Grant Cloud Build permissions
$PROJECT_NUMBER = gcloud projects describe tcu-ceaa-staging --format="value(projectNumber)"
$CLOUD_BUILD_SA = "${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding tcu-ceaa-staging `
  --member="serviceAccount:${CLOUD_BUILD_SA}" `
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding tcu-ceaa-staging `
  --member="serviceAccount:${CLOUD_BUILD_SA}" `
  --role="roles/artifactregistry.writer"
```

#### 3.5.2 Create Build Trigger
```powershell
# Connect GitHub repository
gcloud alpha builds triggers create github `
  --name="tcu-ceaa-staging-deploy" `
  --repo-name="TCU_CEAA" `
  --repo-owner="Syanpole" `
  --branch-pattern="^feature/liveness-detection-live-camera$" `
  --build-config="cloudbuild.yaml" `
  --substitutions='_REGION=us-central1,_REPO_NAME=tcu-ceaa-repo'

# Verify trigger created
gcloud builds triggers list
```

---

## 🧪 Part 4: Testing & Verification

### Step 4.1: Verify GCP Services (15 minutes)

```powershell
# Check all pods are running
kubectl get pods -n tcu-ceaa-staging

# Expected output:
# NAME                             READY   STATUS    RESTARTS   AGE
# backend-xxxxx-xxxxx              2/2     Running   0          5m
# backend-xxxxx-xxxxx              2/2     Running   0          5m
# celery-worker-xxxxx-xxxxx        2/2     Running   0          5m
# celery-worker-xxxxx-xxxxx        2/2     Running   0          5m
# frontend-xxxxx-xxxxx             1/1     Running   0          5m
# frontend-xxxxx-xxxxx             1/1     Running   0          5m

# Check services
kubectl get services -n tcu-ceaa-staging

# Check logs
kubectl logs -n tcu-ceaa-staging -l app=backend --tail=50
kubectl logs -n tcu-ceaa-staging -l app=celery-worker --tail=50

# Test health endpoint
$BACKEND_IP = kubectl get service backend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
curl "http://${BACKEND_IP}/health/"
# Expected: {"status":"ok"}
```

---

### Step 4.2: Verify AWS Services Integration (20 minutes)

#### 4.2.1 Test S3 Connectivity
```powershell
# Get backend pod
$BACKEND_POD = kubectl get pods -n tcu-ceaa-staging -l app=backend -o jsonpath='{.items[0].metadata.name}'

# Test S3 upload
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- python -c @"
import boto3
import os

s3 = boto3.client('s3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_S3_REGION_NAME']
)

# Test upload
s3.put_object(
    Bucket=os.environ['AWS_STORAGE_BUCKET_NAME'],
    Key='test/connection-test.txt',
    Body=b'GCP-AWS connection successful!'
)
print('✅ S3 upload successful')
"@

# Verify file in S3
aws s3 ls s3://tcu-ceaa-staging-documents/test/
```

#### 4.2.2 Test Textract Integration
```powershell
# Test Textract
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- python -c @"
import boto3
import os

textract = boto3.client('textract',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_S3_REGION_NAME']
)

# Test Textract (requires a document in S3)
try:
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': os.environ['AWS_STORAGE_BUCKET_NAME'],
                'Name': 'test/sample-document.jpg'
            }
        }
    )
    print('✅ Textract API accessible')
except Exception as e:
    print(f'⚠️ Textract test: {str(e)}')
"@
```

#### 4.2.3 Test Rekognition Integration
```powershell
# Test Rekognition
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- python -c @"
import boto3
import os

rekognition = boto3.client('rekognition',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_S3_REGION_NAME']
)

# Test Rekognition (requires a face image in S3)
try:
    response = rekognition.detect_faces(
        Image={
            'S3Object': {
                'Bucket': os.environ['AWS_STORAGE_BUCKET_NAME'],
                'Name': 'test/sample-face.jpg'
            }
        }
    )
    print('✅ Rekognition API accessible')
except Exception as e:
    print(f'⚠️ Rekognition test: {str(e)}')
"@
```

---

### Step 4.3: End-to-End Application Testing (30 minutes)

#### 4.3.1 Test Application Flow
```powershell
# Get frontend URL
$FRONTEND_IP = kubectl get service frontend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
Write-Output "Frontend URL: http://${FRONTEND_IP}"

# Get backend URL
$BACKEND_IP = kubectl get service backend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
Write-Output "Backend API URL: http://${BACKEND_IP}"

# Open in browser
Start-Process "http://${FRONTEND_IP}"
```

#### 4.3.2 Test Key Features
1. **User Registration**: Create a new account
2. **Document Upload**: Upload birth certificate (tests S3 + Textract)
3. **ID Upload**: Upload school ID (tests S3 + Rekognition)
4. **Face Verification**: Test liveness detection (tests Rekognition)
5. **Grade Submission**: Submit grades (tests full workflow)

---

## 📊 Part 5: Monitoring & Optimization

### Step 5.1: Set Up Cloud Monitoring (15 minutes)

```powershell
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create uptime check for backend
gcloud monitoring uptime-checks create http backend-health `
  --display-name="TCU CEAA Backend Health" `
  --resource-type=uptime-url `
  --host="${BACKEND_IP}" `
  --path="/health/" `
  --check-interval=60s

# Create uptime check for frontend
gcloud monitoring uptime-checks create http frontend-health `
  --display-name="TCU CEAA Frontend Health" `
  --resource-type=uptime-url `
  --host="${FRONTEND_IP}" `
  --path="/" `
  --check-interval=60s

# View monitoring dashboard
Write-Output "Monitoring Dashboard: https://console.cloud.google.com/monitoring"
```

---

### Step 5.2: Set Up Logging (10 minutes)

```powershell
# Enable Cloud Logging
gcloud services enable logging.googleapis.com

# View logs in Cloud Console
Write-Output "Logs: https://console.cloud.google.com/logs"

# Query logs from CLI
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=tcu-ceaa-staging" `
  --limit=50 `
  --format=json
```

---

### Step 5.3: Cost Optimization Tips

#### 5.3.1 GCP Cost Optimization
```powershell
# Enable committed use discounts for GKE
# 1-year commitment can save 37%, 3-year saves 55%

# Use preemptible nodes for non-critical workloads
gcloud container node-pools create preemptible-pool `
  --cluster=tcu-ceaa-cluster `
  --region=us-central1 `
  --machine-type=e2-medium `
  --num-nodes=1 `
  --preemptible

# Enable cluster autoscaling
gcloud container clusters update tcu-ceaa-cluster `
  --region=us-central1 `
  --enable-autoscaling `
  --min-nodes=1 `
  --max-nodes=5
```

#### 5.3.2 AWS Cost Optimization
- **S3**: Use lifecycle policies to move old documents to Glacier
- **Textract**: Cache OCR results to avoid re-processing
- **Rekognition**: Use face collection for faster searches

---

## 🔒 Part 6: Security Hardening

### Step 6.1: Network Security

```powershell
# Create firewall rules
gcloud compute firewall-rules create allow-backend-health `
  --direction=INGRESS `
  --priority=1000 `
  --network=default `
  --action=ALLOW `
  --rules=tcp:8000 `
  --source-ranges=35.191.0.0/16,130.211.0.0/22 `
  --target-tags=gke-node

# Enable Binary Authorization
gcloud services enable binaryauthorization.googleapis.com
gcloud container clusters update tcu-ceaa-cluster `
  --region=us-central1 `
  --enable-binauthz
```

---

### Step 6.2: Secrets Management

```powershell
# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Migrate secrets to Secret Manager (recommended for production)
echo -n "$AWS_ACCESS_KEY_ID" | gcloud secrets create aws-access-key-id --data-file=-
echo -n "$AWS_SECRET_ACCESS_KEY" | gcloud secrets create aws-secret-access-key --data-file=-
echo -n "$DJANGO_SECRET_KEY" | gcloud secrets create django-secret-key --data-file=-

# Grant access to service account
gcloud secrets add-iam-policy-binding aws-access-key-id `
  --member="serviceAccount:${SA_EMAIL}" `
  --role="roles/secretmanager.secretAccessor"
```

---

## 📈 Part 7: Scaling & Performance

### Step 7.1: Configure Horizontal Pod Autoscaling

```powershell
# Create HPA for backend
kubectl autoscale deployment backend `
  -n tcu-ceaa-staging `
  --cpu-percent=70 `
  --min=2 `
  --max=10

# Create HPA for Celery workers
kubectl autoscale deployment celery-worker `
  -n tcu-ceaa-staging `
  --cpu-percent=75 `
  --min=2 `
  --max=8

# Verify HPA
kubectl get hpa -n tcu-ceaa-staging
```

---

### Step 7.2: Performance Optimization

#### 7.2.1 Enable CDN for Frontend
```powershell
# Enable Cloud CDN for frontend service
gcloud compute backend-services update frontend-backend-service `
  --enable-cdn `
  --cache-mode=CACHE_ALL_STATIC

# Configure cache headers in frontend
```

#### 7.2.2 Database Connection Pooling
- Use PgBouncer for PostgreSQL connection pooling
- Configure in backend settings:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

---

## 🚨 Troubleshooting

### Common Issues

#### Issue 1: Pods CrashLoopBackOff
```powershell
# Check pod logs
kubectl logs -n tcu-ceaa-staging <pod-name>

# Describe pod for events
kubectl describe pod -n tcu-ceaa-staging <pod-name>

# Common fixes:
# - Check secrets are properly configured
# - Verify Cloud SQL proxy is running
# - Check resource limits
```

#### Issue 2: AWS Services Connection Failed
```powershell
# Verify AWS credentials
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- env | grep AWS

# Test AWS connectivity
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- aws s3 ls

# Check IAM policies
aws iam get-user-policy --user-name tcu-ceaa-app --policy-name TCU-CEAA-Textract-Policy
```

#### Issue 3: Database Connection Timeout
```powershell
# Check Cloud SQL proxy
kubectl logs -n tcu-ceaa-staging <pod-name> -c cloud-sql-proxy

# Verify Cloud SQL instance is running
gcloud sql instances describe tcu-ceaa-postgres

# Test connection from pod
kubectl exec -n tcu-ceaa-staging $BACKEND_POD -- pg_isready -h /cloudsql/$SQL_CONNECTION_NAME
```

---

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] GCP project created and billing enabled
- [ ] AWS account configured with IAM user
- [ ] S3 bucket created
- [ ] Textract and Rekognition enabled
- [ ] Docker images built and pushed
- [ ] Kubernetes secrets configured

### Deployment
- [ ] GKE cluster running
- [ ] Cloud SQL (PostgreSQL) accessible
- [ ] Memorystore (Redis) accessible
- [ ] Backend deployed and healthy
- [ ] Celery workers running
- [ ] Frontend deployed and accessible
- [ ] Database migrations completed

### Post-Deployment
- [ ] Application accessible via LoadBalancer IP
- [ ] S3 uploads working
- [ ] Textract OCR functioning
- [ ] Rekognition face verification working
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] DNS configured (if applicable)

---

## 🎯 Production Readiness

### Before Going to Production

1. **Domain & SSL**:
   ```powershell
   # Reserve static IP
   gcloud compute addresses create tcu-ceaa-ip --global
   
   # Configure Cloud DNS
   gcloud dns managed-zones create tcu-ceaa-zone `
     --dns-name="yourdomain.com." `
     --description="TCU CEAA DNS Zone"
   
   # Add SSL certificate
   gcloud compute ssl-certificates create tcu-ceaa-cert `
     --domains="yourdomain.com,www.yourdomain.com"
   ```

2. **Backup Strategy**:
   - Enable automated Cloud SQL backups (daily)
   - Enable S3 versioning and cross-region replication
   - Schedule database dumps to GCS

3. **Disaster Recovery**:
   - Document rollback procedures
   - Create staging environment for testing
   - Set up multi-region deployment

4. **Compliance**:
   - Enable audit logging
   - Configure data retention policies
   - Implement GDPR/privacy controls

---

## 💰 Cost Estimates

### Monthly Costs (Staging Environment)

**GCP Services**:
- GKE Cluster (2 nodes, e2-standard-2): ~$70/month
- Cloud SQL (db-f1-micro): ~$15/month
- Memorystore Redis (1GB): ~$25/month
- Cloud Load Balancer: ~$20/month
- Artifact Registry: ~$1/month
- **GCP Total**: ~$131/month

**AWS Services**:
- S3 Storage (100GB): ~$2.30/month
- S3 Requests (10k/month): ~$0.05/month
- Textract (1k pages/month): ~$15/month
- Rekognition (1k face comparisons/month): ~$10/month
- **AWS Total**: ~$27.35/month

**Grand Total**: ~$158.35/month for staging

**Production estimates**: 3-5x higher depending on traffic

---

## 📚 Additional Resources

### GCP Documentation
- [GKE Quickstart](https://cloud.google.com/kubernetes-engine/docs/quickstart)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)

### AWS Documentation
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [Textract Developer Guide](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
- [Rekognition Face Liveness](https://docs.aws.amazon.com/rekognition/latest/dg/face-liveness.html)

### Kubernetes
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Production Readiness Checklist](https://kubernetes.io/docs/setup/production-environment/)

---

## 🎉 Conclusion

You now have a fully functional hybrid cloud deployment:
- ✅ GCP infrastructure (GKE, Cloud SQL, Memorystore)
- ✅ AWS AI services (S3, Textract, Rekognition)
- ✅ Automated CI/CD with Cloud Build
- ✅ Monitoring and logging
- ✅ Security hardening
- ✅ Cost optimization

### Next Steps
1. Set up production environment
2. Configure custom domain and SSL
3. Implement comprehensive monitoring
4. Set up automated backups
5. Document operational procedures

**Need help?** Check the troubleshooting section or reach out to your cloud provider support.

**Happy deploying! 🚀**
