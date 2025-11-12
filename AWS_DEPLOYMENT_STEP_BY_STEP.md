# 🚀 TCU CEAA - Complete AWS Deployment Guide

## 📅 Timeline: Wednesday → Thursday → Friday

This guide walks you through every step needed to deploy TCU CEAA to AWS staging by Friday.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] AWS Account created and verified
- [ ] Billing enabled (credit card added)
- [ ] AWS CLI installed: `aws --version`
- [ ] kubectl installed: `kubectl version --client`
- [ ] Docker Desktop installed and running
- [ ] Git repository up to date: `git pull origin prep-for-hosting`
- [ ] Backend `.env` file with all credentials
- [ ] Kubernetes secrets generated: `python scripts/generate_k8s_secrets.py staging`

---

## 🗓️ WEDNESDAY: AWS Infrastructure Setup (4-5 hours)

### Step 1: AWS Account Setup (30 minutes)

#### 1.1 Sign in to AWS Console
```
URL: https://aws.amazon.com/console/
Login with your AWS account
```

#### 1.2 Enable Required Services
Go to AWS Services and ensure these are available in your region:
- ✅ **S3** (Object Storage)
- ✅ **EKS** (Kubernetes)
- ✅ **ECR** (Container Registry)
- ✅ **Textract** (OCR Service)
- ✅ **VPC** (Networking)
- ✅ **IAM** (Identity & Access Management)

**Recommended Region**: `us-east-1` (Virginia)
- Lowest cost
- All services available
- Matches your current AWS_S3_REGION_NAME

#### 1.3 Set Up AWS CLI
```powershell
# Install AWS CLI (if not already installed)
# Download from: https://aws.amazon.com/cli/

# Verify installation
aws --version
# Should show: aws-cli/2.x.x

# Configure AWS credentials
aws configure

# You'll be prompted for:
AWS Access Key ID: AKIAWZNMCNNJEXB7DKWK
AWS Secret Access Key: O2YizDIJg+vsunz/IF0Se4dXq/LorI1SpIqfxwIO
Default region name: us-east-1
Default output format: json

# Test connection
aws sts get-caller-identity
# Should show your account details
```

---

### Step 2: Create S3 Bucket for Media Storage (15 minutes)

#### 2.1 Create Staging Bucket
```bash
# Create bucket
aws s3 mb s3://tcu-ceaa-staging-media --region us-east-1

# Verify bucket was created
aws s3 ls | grep tcu-ceaa

# Expected output:
# 2025-11-12 11:00:00 tcu-ceaa-staging-media
```

#### 2.2 Configure Bucket for Django/S3
```bash
# Create bucket policy file
cat > bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDjangoAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_IAM_USER"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::tcu-ceaa-staging-media",
        "arn:aws:s3:::tcu-ceaa-staging-media/*"
      ]
    }
  ]
}
EOF

# Note: Replace YOUR_ACCOUNT_ID with actual account ID
# Get it with: aws sts get-caller-identity --query Account --output text
```

#### 2.3 Enable CORS for S3
```bash
# Create CORS configuration
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://staging.tcu-ceaa.com", "http://localhost:3000"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

# Apply CORS configuration
aws s3api put-bucket-cors --bucket tcu-ceaa-staging-media --cors-configuration file://cors.json

# Verify CORS
aws s3api get-bucket-cors --bucket tcu-ceaa-staging-media
```

#### 2.4 Test S3 Upload
```bash
# Create test file
echo "TCU CEAA Staging Test" > test-upload.txt

# Upload test file
aws s3 cp test-upload.txt s3://tcu-ceaa-staging-media/test/

# List bucket contents
aws s3 ls s3://tcu-ceaa-staging-media/ --recursive

# Download to verify
aws s3 cp s3://tcu-ceaa-staging-media/test/test-upload.txt test-download.txt

# Clean up test
aws s3 rm s3://tcu-ceaa-staging-media/test/test-upload.txt
rm test-upload.txt test-download.txt
```

**✅ Checkpoint**: S3 bucket created and tested

---

### Step 3: Verify AWS Textract Access (10 minutes)

#### 3.1 Check Textract Availability
```bash
# Test Textract API
aws textract help

# Check if service is available in your region
aws textract detect-document-text --help
```

#### 3.2 Test Textract with Sample Document
```bash
# Create a simple test image with text
# Or use an existing document from your media folder

# Test Textract OCR
aws textract detect-document-text \
  --document '{"S3Object":{"Bucket":"tcu-ceaa-staging-media","Name":"test/sample.jpg"}}' \
  --region us-east-1

# If successful, you'll see JSON output with detected text
```

**Note**: Textract costs ~$0.0015 per page. Your Django app already uses it via `USE_ADVANCED_OCR=True`

**✅ Checkpoint**: Textract API accessible

---

### Step 4: Create ECR (Elastic Container Registry) (20 minutes)

#### 4.1 Create Repositories for Docker Images
```bash
# Create repository for backend
aws ecr create-repository \
  --repository-name tcu-ceaa/backend \
  --region us-east-1

# Create repository for celery worker
aws ecr create-repository \
  --repository-name tcu-ceaa/celery \
  --region us-east-1

# Create repository for frontend
aws ecr create-repository \
  --repository-name tcu-ceaa/frontend \
  --region us-east-1

# List repositories
aws ecr describe-repositories --region us-east-1
```

#### 4.2 Get ECR Login Credentials
```bash
# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Replace YOUR_ACCOUNT_ID with your actual account ID:
# Get it with: aws sts get-caller-identity --query Account --output text

# Example:
# 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

#### 4.3 Set Environment Variable for Registry
```powershell
# PowerShell (Windows)
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$env:REGISTRY = "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"
echo $env:REGISTRY

# Save for later use
echo "REGISTRY=$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com" >> registry.env
```

**✅ Checkpoint**: ECR repositories created and ready

---

### Step 5: Create EKS Cluster (1-2 hours)

#### 5.1 Install eksctl (if not installed)
```powershell
# Windows (using Chocolatey)
choco install eksctl

# Or download from: https://eksctl.io/

# Verify installation
eksctl version
```

#### 5.2 Create EKS Cluster Configuration
```yaml
# Create file: eks-staging-cluster.yaml
cat > eks-staging-cluster.yaml << 'EOF'
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: tcu-ceaa-staging
  region: us-east-1
  version: "1.28"

managedNodeGroups:
  - name: staging-nodes
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 1
    maxSize: 3
    volumeSize: 20
    ssh:
      allow: false
    labels:
      environment: staging
    tags:
      Environment: staging
      Project: tcu-ceaa

# Enable logging
cloudWatch:
  clusterLogging:
    enableTypes:
      - api
      - audit
      - authenticator
EOF
```

#### 5.3 Create the Cluster
```bash
# This takes 15-20 minutes!
eksctl create cluster -f eks-staging-cluster.yaml

# Monitor progress (in another terminal)
watch kubectl get nodes

# Expected output after completion:
# NAME                         STATUS   ROLES    AGE   VERSION
# ip-192-168-x-x.ec2.internal  Ready    <none>   5m    v1.28.x
# ip-192-168-y-y.ec2.internal  Ready    <none>   5m    v1.28.x
```

#### 5.4 Verify Cluster Connection
```bash
# Update kubeconfig
aws eks update-kubeconfig --name tcu-ceaa-staging --region us-east-1

# Test connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check namespaces
kubectl get namespaces
```

**✅ Checkpoint**: EKS cluster running with 2 nodes

---

### Step 6: Set Up IAM Permissions (30 minutes)

#### 6.1 Create IAM Policy for Application
```bash
# Create policy document
cat > tcu-ceaa-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::tcu-ceaa-staging-media",
        "arn:aws:s3:::tcu-ceaa-staging-media/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "textract:DetectDocumentText",
        "textract:AnalyzeDocument"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create IAM policy
aws iam create-policy \
  --policy-name TCU-CEAA-Staging-Policy \
  --policy-document file://tcu-ceaa-policy.json

# Note the ARN from output, you'll need it
```

#### 6.2 Attach Policy to Your IAM User
```bash
# Get your IAM username
aws iam get-user --query User.UserName --output text

# Attach policy (replace YOUR_ACCOUNT_ID and YOUR_USERNAME)
aws iam attach-user-policy \
  --user-name YOUR_USERNAME \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/TCU-CEAA-Staging-Policy

# Verify policies attached
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

**✅ Checkpoint**: IAM permissions configured

---

### Step 7: Cost Optimization & Monitoring (15 minutes)

#### 7.1 Set Up Billing Alerts
```
1. Go to AWS Console → Billing Dashboard
2. Click "Billing preferences"
3. Enable "Receive Free Tier Usage Alerts"
4. Enable "Receive Billing Alerts"
5. Enter your email address
6. Save preferences

7. Go to CloudWatch → Alarms → Create Alarm
8. Select "Billing" metric
9. Set threshold: $50 USD
10. Create SNS topic for notifications
11. Enter your email
12. Create alarm
```

#### 7.2 Estimated Monthly Costs (Staging)
```
EKS Cluster (Control Plane):    $73/month
EC2 Instances (2 × t3.medium):  $60/month
EBS Storage (40 GB):            $4/month
S3 Storage (10 GB):             $0.23/month
Data Transfer (50 GB):          $4.50/month
Textract (1000 pages):          $1.50/month
Load Balancer:                  $16/month
----------------------------------------
TOTAL:                          ~$160/month
```

**Cost Saving Tips**:
- Stop cluster when not testing: Save ~$130/month
- Use t3.small instead of t3.medium: Save $30/month
- Delete after Friday demo: No ongoing costs

**✅ Checkpoint**: Billing alerts configured

---

## 📝 End of Wednesday Summary

At this point, you should have:
- ✅ AWS CLI configured and working
- ✅ S3 bucket: `tcu-ceaa-staging-media` created and tested
- ✅ Textract API verified
- ✅ ECR repositories created (3 repos)
- ✅ EKS cluster running (2 nodes)
- ✅ IAM permissions configured
- ✅ Billing alerts set up
- ✅ kubectl connected to cluster

**Save these for Thursday**:
```bash
# Save your registry URL
echo "REGISTRY=YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"

# Save cluster name
echo "CLUSTER=tcu-ceaa-staging"

# Save region
echo "REGION=us-east-1"
```

---

## 🗓️ THURSDAY: Build & Deploy (4-5 hours)

### Step 1: Build Docker Images (1 hour)

#### 1.1 Login to ECR
```bash
# Get fresh credentials (they expire after 12 hours)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
```

#### 1.2 Build Backend Image
```bash
cd d:\Python\TCU_CEAA

# Set registry variable
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$REGISTRY = "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"

# Build backend
docker build -f backend/Dockerfile.prod -t $REGISTRY/tcu-ceaa/backend:staging ./backend

# This takes 5-10 minutes
# You'll see output like:
# Step 1/15 : FROM python:3.11-slim
# Step 2/15 : RUN apt-get update...
# ...
# Successfully built abc123def456
# Successfully tagged 123456789012.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/backend:staging
```

#### 1.3 Build Celery Worker Image
```bash
# Build celery worker (ML/AI tasks)
docker build -f backend/Dockerfile.celery -t $REGISTRY/tcu-ceaa/celery:staging ./backend

# This takes 10-15 minutes (includes YOLOv8, OpenCV, etc.)
```

#### 1.4 Build Frontend Image
```bash
# Build frontend
docker build -f frontend/Dockerfile.prod -t $REGISTRY/tcu-ceaa/frontend:staging ./frontend

# This takes 5-10 minutes
```

#### 1.5 Push Images to ECR
```bash
# Push backend
docker push $REGISTRY/tcu-ceaa/backend:staging

# Push celery
docker push $REGISTRY/tcu-ceaa/celery:staging

# Push frontend
docker push $REGISTRY/tcu-ceaa/frontend:staging

# Each push takes 2-5 minutes depending on image size
```

#### 1.6 Verify Images in ECR
```bash
# List images in each repository
aws ecr describe-images --repository-name tcu-ceaa/backend --region us-east-1
aws ecr describe-images --repository-name tcu-ceaa/celery --region us-east-1
aws ecr describe-images --repository-name tcu-ceaa/frontend --region us-east-1

# You should see imageTags: ["staging"]
```

**✅ Checkpoint**: All 3 Docker images built and pushed to ECR

---

### Step 2: Update Kubernetes Manifests with Registry URLs (15 minutes)

#### 2.1 Update Backend Deployment
```bash
cd d:\Python\TCU_CEAA

# Get your registry URL
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$REGISTRY = "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"

# Update k8s/staging/04-backend.yaml
# Find line with: image: YOUR_REGISTRY/tcu-ceaa-backend:staging
# Replace YOUR_REGISTRY with your actual registry URL
```

Edit `k8s/staging/04-backend.yaml`:
```yaml
# Change this:
image: YOUR_REGISTRY/tcu-ceaa-backend:staging

# To this (replace 123456789012 with your account ID):
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/backend:staging
```

#### 2.2 Update Celery Deployment
Edit `k8s/staging/05-celery-worker.yaml`:
```yaml
# Change this:
image: YOUR_REGISTRY/tcu-ceaa-celery:staging

# To this:
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/celery:staging
```

#### 2.3 Update Frontend Deployment
Edit `k8s/staging/06-frontend.yaml`:
```yaml
# Change this:
image: YOUR_REGISTRY/tcu-ceaa-frontend:staging

# To this:
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/frontend:staging
```

#### 2.4 Quick PowerShell Script to Update All
```powershell
# Or use this script to update all at once:
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$REGISTRY = "$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com"

# Update backend
(Get-Content k8s/staging/04-backend.yaml) -replace 'YOUR_REGISTRY', $REGISTRY | Set-Content k8s/staging/04-backend.yaml

# Update celery
(Get-Content k8s/staging/05-celery-worker.yaml) -replace 'YOUR_REGISTRY', $REGISTRY | Set-Content k8s/staging/05-celery-worker.yaml

# Update frontend
(Get-Content k8s/staging/06-frontend.yaml) -replace 'YOUR_REGISTRY', $REGISTRY | Set-Content k8s/staging/06-frontend.yaml

# Verify changes
Select-String -Path k8s/staging/*.yaml -Pattern 'image:' | Select-Object -First 5
```

**✅ Checkpoint**: Kubernetes manifests updated with ECR URLs

---

### Step 3: Deploy to Kubernetes (30 minutes)

#### 3.1 Apply Secrets First
```bash
# Ensure secrets are generated
python scripts/generate_k8s_secrets.py staging

# Apply secrets to cluster
kubectl apply -f k8s/staging/01-secrets.yaml

# Verify secrets created
kubectl get secrets -n tcu-ceaa-staging

# Expected output:
# NAME                TYPE     DATA   AGE
# tcu-ceaa-secrets    Opaque   10     5s
```

#### 3.2 Deploy All Services in Order
```bash
# 1. Create namespace
kubectl apply -f k8s/staging/00-namespace.yaml

# 2. Apply ConfigMap and Secrets (already done above)
kubectl get configmap -n tcu-ceaa-staging

# 3. Deploy PostgreSQL
kubectl apply -f k8s/staging/02-postgres.yaml

# Wait for postgres to be ready (2-3 minutes)
kubectl wait --for=condition=ready pod -l app=postgres -n tcu-ceaa-staging --timeout=300s

# 4. Deploy Redis
kubectl apply -f k8s/staging/03-redis.yaml

# Wait for redis
kubectl wait --for=condition=ready pod -l app=redis -n tcu-ceaa-staging --timeout=120s

# 5. Deploy Backend
kubectl apply -f k8s/staging/04-backend.yaml

# Wait for backend (5-7 minutes for migrations to run)
kubectl wait --for=condition=ready pod -l app=backend -n tcu-ceaa-staging --timeout=600s

# 6. Deploy Celery Worker
kubectl apply -f k8s/staging/05-celery-worker.yaml

# 7. Deploy Frontend
kubectl apply -f k8s/staging/06-frontend.yaml

# 8. Deploy Ingress/Load Balancer
kubectl apply -f k8s/staging/07-ingress.yaml
```

#### 3.3 Monitor Deployment Progress
```bash
# Watch all pods starting up
kubectl get pods -n tcu-ceaa-staging -w

# In another terminal, check logs
kubectl logs -f deployment/backend -n tcu-ceaa-staging

# Expected pod states after 10-15 minutes:
# postgres-0                  1/1     Running
# redis-xxxxx                 1/1     Running
# backend-xxxxx               1/1     Running
# backend-yyyyy               1/1     Running
# celery-worker-xxxxx         1/1     Running
# frontend-xxxxx              1/1     Running
```

#### 3.4 Troubleshoot if Pods Fail
```bash
# Check pod status
kubectl get pods -n tcu-ceaa-staging

# If any pod is not Running:
kubectl describe pod POD_NAME -n tcu-ceaa-staging

# Check logs
kubectl logs POD_NAME -n tcu-ceaa-staging

# Common issues:
# - ImagePullBackOff: ECR authentication expired or wrong image URL
# - CrashLoopBackOff: Check logs for errors
# - Pending: Insufficient cluster resources
```

**✅ Checkpoint**: All pods running successfully

---

### Step 4: Get Application URL (10 minutes)

#### 4.1 Get LoadBalancer URL
```bash
# Get frontend service
kubectl get svc -n tcu-ceaa-staging

# Look for frontend-service with EXTERNAL-IP
# NAME               TYPE           EXTERNAL-IP                            PORT(S)
# frontend-service   LoadBalancer   a1b2c3d4.us-east-1.elb.amazonaws.com   80:30xxx/TCP

# Get the URL
kubectl get svc frontend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Save this URL!
```

#### 4.2 Wait for DNS Propagation (5-10 minutes)
```bash
# Test if LoadBalancer is ready
$FRONTEND_URL = kubectl get svc frontend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Try to access (may take a few minutes)
curl http://$FRONTEND_URL

# Or open in browser:
# http://a1b2c3d4.us-east-1.elb.amazonaws.com
```

#### 4.3 Test Backend Health
```bash
# Get backend service URL
$BACKEND_URL = kubectl get svc backend-service -n tcu-ceaa-staging -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test health endpoint
curl http://$BACKEND_URL:8000/health/

# Should return:
# {"status": "healthy", "database": "connected", "cache": "connected"}
```

**✅ Checkpoint**: Application accessible via LoadBalancer URL

---

### Step 5: Create Django Superuser (10 minutes)

#### 5.1 Get Backend Pod Name
```bash
# List backend pods
kubectl get pods -n tcu-ceaa-staging -l app=backend

# Pick one pod name
# Example: backend-7d8f9c5b6-xk2lm
```

#### 5.2 Create Superuser
```bash
# Access pod shell
kubectl exec -it backend-7d8f9c5b6-xk2lm -n tcu-ceaa-staging -- /bin/bash

# Inside the pod:
python manage.py createsuperuser

# Enter details:
Username: admin
Email: admin@tcu-ceaa.edu.ph
Password: (create a strong password)
Password (again): (repeat)

# Exit pod
exit
```

#### 5.3 Test Admin Access
```
1. Open browser
2. Go to: http://YOUR_LOADBALANCER_URL/admin/
3. Login with admin credentials
4. You should see Django admin dashboard
```

**✅ Checkpoint**: Admin user created and working

---

## 📝 End of Thursday Summary

At this point, you should have:
- ✅ 3 Docker images built and pushed to ECR
- ✅ All Kubernetes manifests deployed
- ✅ 6 pods running (postgres, redis, 2 backend, celery, frontend)
- ✅ LoadBalancer with public URL
- ✅ Admin user created
- ✅ Health checks passing

**Save these URLs**:
```
Frontend: http://your-frontend-lb-url.elb.amazonaws.com
Backend API: http://your-backend-lb-url.elb.amazonaws.com
Admin: http://your-frontend-lb-url.elb.amazonaws.com/admin/
```

---

## 🗓️ FRIDAY: Testing & Launch (2-3 hours)

### Step 1: Comprehensive Testing (1.5 hours)

Follow `STAGING_CHECKLIST.md` for complete testing:

#### 1.1 Student Registration Flow
```
1. Open frontend URL
2. Click "Register"
3. Enter student details:
   - Email: test@tcu.edu.ph
   - Password: TestPass123!
   - Student ID: 2024-12345
4. Submit registration
5. Check email for verification link
6. Click verification link
7. Login with credentials
```

#### 1.2 Document Upload & AI Verification
```
1. After login, go to Dashboard
2. Upload COE document (PDF or JPG)
   - Use a real sample from backend/media/
3. Wait 30-60 seconds for AI processing
4. Check document status:
   - ✅ APPROVED (if confidence > 80%)
   - ❌ REJECTED (if confidence < 80%)
5. View confidence score and extracted data
6. Repeat for ID document
```

#### 1.3 Full Application Submission
```
1. Complete basic qualification
2. Upload all required documents
3. Fill grade information
4. Submit full application
5. Check email for confirmation
6. Verify application appears in admin dashboard
```

#### 1.4 Admin Review
```
1. Login to admin: /admin/
2. Navigate to Applications
3. Review student submissions
4. Check AI verification results
5. Approve/reject applications
6. Verify student receives email notification
```

#### 1.5 Backend Testing
```bash
# Test health endpoints
curl http://YOUR_BACKEND_URL/health/
curl http://YOUR_BACKEND_URL/readiness/
curl http://YOUR_BACKEND_URL/liveness/

# Check logs for errors
kubectl logs -f deployment/backend -n tcu-ceaa-staging

# Monitor Celery tasks
kubectl logs -f deployment/celery-worker -n tcu-ceaa-staging

# Check database
kubectl exec -it postgres-0 -n tcu-ceaa-staging -- psql -U postgres -d tcu_ceaa_staging -c "SELECT COUNT(*) FROM myapp_student;"
```

**✅ Checkpoint**: All features tested and working

---

### Step 2: Performance & Monitoring (30 minutes)

#### 2.1 Check Resource Usage
```bash
# Pod resource usage
kubectl top pods -n tcu-ceaa-staging

# Node resource usage
kubectl top nodes

# Expected usage:
# backend:      200-400 MB RAM, 100-300m CPU
# celery:       800-1500 MB RAM, 500-1000m CPU
# postgres:     100-200 MB RAM, 50-100m CPU
# redis:        30-50 MB RAM, 10-20m CPU
# frontend:     20-40 MB RAM, 10-20m CPU
```

#### 2.2 Check Logs for Errors
```bash
# Backend errors
kubectl logs deployment/backend -n tcu-ceaa-staging | grep -i error

# Celery errors
kubectl logs deployment/celery-worker -n tcu-ceaa-staging | grep -i error

# Database errors
kubectl logs statefulset/postgres -n tcu-ceaa-staging | grep -i error
```

#### 2.3 Load Testing (Optional)
```bash
# Simple load test
for i in {1..10}; do
  curl -s http://YOUR_BACKEND_URL/health/ &
done
wait

# Or use Apache Bench
ab -n 100 -c 10 http://YOUR_BACKEND_URL/health/
```

**✅ Checkpoint**: Performance acceptable, no errors

---

### Step 3: Documentation & Handoff (30 minutes)

#### 3.1 Document Production URLs
```
Frontend: http://YOUR_FRONTEND_LB.elb.amazonaws.com
Backend API: http://YOUR_BACKEND_LB.elb.amazonaws.com:8000
Admin: http://YOUR_FRONTEND_LB.elb.amazonaws.com/admin/

Admin Credentials:
Username: admin
Password: [SECURE PASSWORD]

Test Student Account:
Email: test@tcu.edu.ph
Password: TestPass123!
```

#### 3.2 Create Launch Announcement
```markdown
🚀 TCU CEAA Staging Environment is LIVE!

Frontend: http://[YOUR-URL]
Admin: http://[YOUR-URL]/admin

Features Available:
✅ Student registration & email verification
✅ Document upload (COE, ID)
✅ AI-powered document verification (89% accuracy)
✅ Grade submission
✅ Full application workflow
✅ Admin review dashboard

Known Limitations (Manual Review):
⚠️ Birth certificate verification
⚠️ Voter's certificate verification  
⚠️ Liveness/face detection

Test Credentials:
Admin: admin / [password]
Student: test@tcu.edu.ph / TestPass123!

Please test and report issues!
```

#### 3.3 Monitoring Plan
```
Daily:
- Check pod status: kubectl get pods -n tcu-ceaa-staging
- Review logs for errors
- Monitor AWS billing

Weekly:
- Review user feedback
- Update documentation
- Plan for missing features

After Demo:
- Decision: Keep running or shut down
- If keeping: Set up proper domain + SSL
- If shutting down: Delete cluster to save costs
```

**✅ Checkpoint**: Documentation complete

---

## 📊 Success Criteria

Before announcing "STAGING READY":

- [ ] All 6 pods in Running state
- [ ] Frontend accessible via LoadBalancer URL
- [ ] Backend /health/ returns 200 OK
- [ ] Can register new user
- [ ] Email verification works
- [ ] Can upload COE document
- [ ] COE AI verification completes (shows confidence %)
- [ ] Can upload ID document
- [ ] ID AI verification completes
- [ ] Can submit grades
- [ ] Can submit full application
- [ ] Admin can login and review applications
- [ ] Email notifications working
- [ ] No critical errors in logs
- [ ] AWS costs under $10/day

---

## 🚨 Common Issues & Solutions

### Issue 1: Pods stuck in ImagePullBackOff
**Cause**: ECR authentication expired or wrong image URL

**Solution**:
```bash
# Re-authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Check image URLs in manifests
grep "image:" k8s/staging/*.yaml

# Restart deployment
kubectl rollout restart deployment/backend -n tcu-ceaa-staging
```

### Issue 2: Backend pod CrashLoopBackOff
**Cause**: Database connection failed or migrations failed

**Solution**:
```bash
# Check logs
kubectl logs deployment/backend -n tcu-ceaa-staging

# Check if postgres is running
kubectl get pods -n tcu-ceaa-staging -l app=postgres

# Check database connection from backend pod
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- python manage.py dbshell

# Run migrations manually
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- python manage.py migrate
```

### Issue 3: S3 upload fails (403 Forbidden)
**Cause**: IAM permissions not set correctly

**Solution**:
```bash
# Verify IAM policy attached
aws iam list-attached-user-policies --user-name YOUR_USERNAME

# Test S3 access from pod
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- bash
# Inside pod:
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.save('test.txt', ContentFile('test'))
```

### Issue 4: Textract returns access denied
**Cause**: IAM policy missing Textract permissions

**Solution**:
```bash
# Add Textract policy
cat > textract-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["textract:*"],
    "Resource": "*"
  }]
}
EOF

aws iam put-user-policy --user-name YOUR_USERNAME --policy-name TextractAccess --policy-document file://textract-policy.json
```

### Issue 5: Email not sending
**Cause**: Gmail app password incorrect or 2FA not enabled

**Solution**:
```bash
# Verify credentials in secret
kubectl get secret tcu-ceaa-secrets -n tcu-ceaa-staging -o jsonpath='{.data.EMAIL_HOST_USER}' | base64 -d

# Test from pod
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Check Gmail settings:
# 1. 2-Step Verification enabled
# 2. App password generated
# 3. "Less secure app access" OFF (use app password)
```

### Issue 6: LoadBalancer stuck in Pending
**Cause**: AWS limits or networking issues

**Solution**:
```bash
# Check service events
kubectl describe svc frontend-service -n tcu-ceaa-staging

# Check AWS LoadBalancer limits
aws elbv2 describe-load-balancers --region us-east-1

# Recreate service
kubectl delete svc frontend-service -n tcu-ceaa-staging
kubectl apply -f k8s/staging/06-frontend.yaml
```

---

## 💰 Cost Management

### Daily Costs (Running 24/7)
```
EKS Control Plane:     $2.40/day ($73/month)
EC2 Instances:         $2.00/day ($60/month)
EBS Storage:           $0.13/day ($4/month)
Load Balancers:        $0.53/day ($16/month)
Data Transfer:         $0.15/day ($4.50/month)
Total:                 ~$5.20/day or $160/month
```

### Cost Saving Options

#### Option 1: Stop Cluster When Not Testing
```bash
# Scale down all deployments
kubectl scale deployment --all --replicas=0 -n tcu-ceaa-staging

# Stop nodes (but keep cluster)
eksctl scale nodegroup --cluster=tcu-ceaa-staging --name=staging-nodes --nodes=0

# Savings: ~$2/day (EC2 costs)
# Still paying: $2.40/day for EKS control plane
```

#### Option 2: Delete Cluster After Demo
```bash
# Delete everything
eksctl delete cluster --name tcu-ceaa-staging --region us-east-1

# Keep S3 bucket (costs pennies)
# Savings: $5.20/day
```

#### Option 3: Use Fargate (Serverless)
```
Replace EC2 nodes with Fargate
Pay only when pods are running
Cost: ~$3/day vs $5.20/day
```

### Set Up Cost Alerts
```
1. AWS Console → Billing → Budgets
2. Create Budget
3. Set monthly budget: $200
4. Set alert at 80% ($160)
5. Add email notification
```

---

## 📚 Additional Resources

### AWS Documentation
- EKS: https://docs.aws.amazon.com/eks/
- S3: https://docs.aws.amazon.com/s3/
- Textract: https://docs.aws.amazon.com/textract/
- ECR: https://docs.aws.amazon.com/ecr/

### Kubernetes Resources
- kubectl cheat sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Pod troubleshooting: https://kubernetes.io/docs/tasks/debug/

### Project Documentation
- DEPLOYMENT_GUIDE.md - Full production guide
- STAGING_CHECKLIST.md - Testing checklist
- SECRETS_MANAGEMENT_GUIDE.md - Security practices
- KUBERNETES_README.md - Quick K8s commands

---

## ✅ Final Checklist

Before announcing "STAGING LIVE":

- [ ] AWS account configured
- [ ] S3 bucket created and tested
- [ ] ECR repositories created
- [ ] EKS cluster running
- [ ] IAM permissions configured
- [ ] Billing alerts set up
- [ ] Docker images built and pushed
- [ ] Kubernetes secrets applied
- [ ] All pods running
- [ ] LoadBalancer URL accessible
- [ ] Admin user created
- [ ] Student registration works
- [ ] Document upload works
- [ ] AI verification works (COE + ID)
- [ ] Email notifications work
- [ ] Admin dashboard accessible
- [ ] No critical errors in logs
- [ ] Documentation completed
- [ ] Team notified

---

## 🎉 Congratulations!

If you've completed all steps, you now have:
- ✅ Fully functional staging environment
- ✅ Running on AWS with Kubernetes
- ✅ AI-powered document verification
- ✅ Scalable microservices architecture
- ✅ Ready for production deployment

**Total Time**: 10-12 hours spread over 3 days
**Total Cost**: ~$160/month (or less with optimizations)

**Next Steps**:
1. Gather user feedback
2. Implement missing features (birth cert, voter's cert, liveness)
3. Plan production deployment with custom domain + SSL
4. Set up CI/CD pipeline for automatic deployments

---

**Questions or issues?** Check the troubleshooting section or review the logs!

**Good luck with your Friday launch! 🚀**
