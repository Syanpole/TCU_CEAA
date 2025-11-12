# TCU-CEAA Deployment Preparation Guide

**Branch**: `prep-for-hosting`  
**Status**: ✅ Preparation Complete - Ready for Deployment Review  
**Last Updated**: November 12, 2025

---

## 📋 Overview

This guide documents all preparation work completed for deploying the TCU-CEAA Certificate of Enrollment and Academic Achievement Auto-Approval System to AWS. The system is ready for deployment review and testing.

---

## 🎯 System Architecture

### Application Stack
- **Backend**: Django 5.2.5 REST API
- **Frontend**: React + TypeScript with Nginx
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL 15
- **AI/ML**: YOLOv8, EasyOCR, PyTorch (CPU-only for cost efficiency)
- **Cloud**: AWS (S3, ECR, EKS, Textract)

### AI Capabilities (Current)
- ✅ **Certificate of Enrollment (COE)**: 89.10% accuracy
- ✅ **School ID Verification**: 89.3% accuracy
- ⏸️ **Birth Certificate**: Disabled (pending implementation)
- ⏸️ **Voter's Certificate**: Disabled (pending implementation)
- ⏸️ **Liveness Detection**: Disabled (pending implementation)

---

## 🐳 Docker Images

### Production Images Built

| Service | Image | Size | Base | Purpose |
|---------|-------|------|------|---------|
| **Backend** | `tcu-ceaa/backend:staging` | 2.59 GB | python:3.11-slim | Django API server |
| **Celery** | `tcu-ceaa/celery:staging` | 4.46 GB | python:3.11-slim | ML/AI task worker (CPU-only PyTorch) |
| **Frontend** | `tcu-ceaa/frontend:staging` | 86.2 MB | nginx:alpine | React SPA |

### Key Improvements Made
1. **Fixed Debian Trixie Compatibility**: Changed `libgl1-mesa-glx` → `libgl1`
2. **CPU-Only PyTorch**: Eliminated 10GB of CUDA libraries (4.46GB vs 14.4GB)
3. **Multi-Stage Builds**: Optimized frontend image size
4. **Security**: Non-root users, minimal base images

### Dockerfile Locations
```
backend/
├── Dockerfile              # Local development
├── Dockerfile.prod         # Production API server
└── Dockerfile.celery       # Production ML worker

frontend/
├── Dockerfile              # Local development
└── Dockerfile.prod         # Production static serving
```

---

## ☸️ Kubernetes Configuration

### Namespace Structure
- **Staging**: `tcu-ceaa-staging` (minimal resources for testing)
- **Production**: `tcu-ceaa-production` (autoscaling, high availability)

### Staging Resources (7 Manifests)

| Manifest | Purpose | Replicas | Resources |
|----------|---------|----------|-----------|
| `00-namespace.yaml` | Namespace definition | N/A | N/A |
| `01-secrets.yaml` | Credentials (generated locally, not in Git) | N/A | N/A |
| `02-postgres.yaml` | Database | 1 | 256Mi-512Mi RAM |
| `03-redis.yaml` | Task queue | 1 | 64Mi-128Mi RAM |
| `04-backend.yaml` | Django API | 2 | 512Mi-1Gi RAM each |
| `05-celery-worker.yaml` | ML processor | 1 | 1.5Gi-3Gi RAM |
| `06-frontend.yaml` | React app | 1 | 64Mi-128Mi RAM |
| `07-ingress.yaml` | Load balancer | N/A | N/A |

**Total Staging Requirements**:
- **Requests**: 3.4 GB RAM, 2.5 CPUs
- **Limits**: 7 GB RAM, 5 CPUs
- **Recommended Node**: t3.xlarge (4 vCPU, 16GB RAM) or t3.2xlarge (8 vCPU, 32GB RAM)

### Production Resources (7 Manifests)
- **Higher Replicas**: Backend (3), Frontend (2), Celery (2-8 autoscaling)
- **Horizontal Pod Autoscaler**: CPU/memory-based scaling
- **Persistent Storage**: Production-grade PVCs
- **Resource Limits**: Production-grade allocations

---

## 🔐 Secrets Management

### Strategy
1. **Local .env File**: Contains real credentials (gitignored)
2. **Generate K8s Secrets**: Python script converts .env to base64 K8s YAML
3. **Never Commit Secrets**: `k8s/**/01-secrets.yaml` is gitignored
4. **GitHub Actions Secrets**: Optional sync script for CI/CD

### Generate Secrets
```powershell
# Generate Kubernetes secrets from .env file
python scripts/generate_k8s_secrets.py staging

# Output: k8s/staging/01-secrets.yaml (gitignored)
```

### Required Environment Variables
```bash
# Database
POSTGRES_DB=tcu_ceaa
POSTGRES_USER=tcu_ceaa_user
POSTGRES_PASSWORD=<your-secure-password>
DATABASE_HOST=postgres-service
DATABASE_PORT=5432

# Django
SECRET_KEY=<django-secret-key>
DEBUG=False
ALLOWED_HOSTS=.tcu-ceaa.edu.ph

# AWS
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_STORAGE_BUCKET_NAME=tcu-ceaa-staging-media
AWS_S3_REGION_NAME=us-east-1

# Email
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<app-password>

# Redis
REDIS_URL=redis://redis-service:6379/0
```

---

## 🚀 AWS Infrastructure Setup

### Prerequisites Completed
✅ AWS CLI v2.31.34 installed  
✅ IAM User: TCU-CEAA configured  
✅ AWS Account: 466901691218  
✅ Region: us-east-1

### AWS Resources Created

#### S3 Buckets
- `tcu-ceaa-documents` (production media storage)
- `tcu-ceaa-staging-media` (staging media storage)

#### ECR Repositories
```
466901691218.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/backend
466901691218.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/celery
466901691218.dkr.ecr.us-east-1.amazonaws.com/tcu-ceaa/frontend
```

#### AWS Textract
- Configured for OCR document extraction
- 90-98% accuracy on certificate text extraction

### Next Steps (Not Yet Done - Deployment Phase)
⏸️ Push Docker images to ECR  
⏸️ Install eksctl and kubectl  
⏸️ Create EKS cluster  
⏸️ Deploy to Kubernetes  
⏸️ Configure DNS and SSL  

---

## 📦 Deployment Scripts

### Available Scripts

#### `scripts/push-images-to-ecr.ps1`
Pushes all three Docker images to AWS ECR with progress tracking.

```powershell
# Usage
.\scripts\push-images-to-ecr.ps1
```

**Features**:
- Verifies all images exist before pushing
- Shows progress for each image
- Displays timing information
- Error handling and validation

**Expected Duration**: 30-60 minutes (depending on network speed)

#### `scripts/generate_k8s_secrets.py`
Converts `.env` file to Kubernetes secrets YAML.

```powershell
# Generate staging secrets
python scripts/generate_k8s_secrets.py staging

# Generate production secrets
python scripts/generate_k8s_secrets.py production
```

**Output**: `k8s/staging/01-secrets.yaml` or `k8s/production/01-secrets.yaml`

---

## 📚 Documentation Files

### Deployment Guides
1. **`AWS_DEPLOYMENT_STEP_BY_STEP.md`** (1200+ lines)
   - Complete AWS deployment walkthrough
   - Day-by-day timeline (Wed/Thu/Fri)
   - Troubleshooting guide
   - Cost estimates

2. **`STAGING_CHECKLIST.md`**
   - Interactive deployment checklist
   - 50+ verification steps
   - Testing procedures

3. **`SECRETS_MANAGEMENT_GUIDE.md`**
   - Security best practices
   - Secret rotation procedures
   - Access control guidelines

4. **`DEPLOYMENT_GUIDE.md`**
   - Production deployment procedures
   - Rollback strategies
   - Monitoring setup

5. **`KUBERNETES_README.md`**
   - Quick K8s commands reference
   - Troubleshooting common issues
   - Scaling procedures

---

## 🧪 Testing Strategy

### Local Testing (Before Deployment)
1. **Docker Compose**: Test all services locally
   ```bash
   docker-compose up
   ```

2. **Unit Tests**: Run Django test suite
   ```bash
   python manage.py test
   ```

3. **AI Model Validation**: Test document verification
   ```bash
   python test_ai_system_simple.py
   ```

### Staging Testing (After Deployment)
1. **Health Checks**: Verify all pods running
2. **Database Migrations**: Confirm schema is up-to-date
3. **File Uploads**: Test S3 integration
4. **AI Processing**: Submit test documents
5. **Email Notifications**: Verify SMTP working
6. **Performance**: Load testing with k6/Locust

---

## 🔧 Configuration Files Modified

### Dockerfiles
- ✅ `backend/Dockerfile.prod`: Fixed libgl1, optimized layers
- ✅ `backend/Dockerfile.celery`: CPU-only PyTorch, removed CUDA
- ✅ `frontend/Dockerfile.prod`: Changed npm ci → npm install

### Requirements Files
- ✅ `backend/requirements-autonomous-ai-cpu.txt`: CPU-only PyTorch dependencies
- ✅ `backend/requirements-autonomous-ai-staging.txt`: Staging dependencies (no face-recognition)

### Kubernetes Manifests
- ✅ `k8s/staging/04-backend.yaml`: Increased memory 256Mi→512Mi (requests), 512Mi→1Gi (limits)
- ✅ `k8s/staging/05-celery-worker.yaml`: Increased memory 512Mi→1.5Gi (requests), 1Gi→3Gi (limits)

### Documentation
- ✅ `AWS_DEPLOYMENT_STEP_BY_STEP.md`: Updated with actual AWS account details

---

## 📊 Cost Estimates

### Staging Environment (Monthly)
- **EKS Cluster**: ~$73/month (control plane)
- **EC2 Nodes**: ~$60/month (1x t3.xlarge)
- **S3 Storage**: ~$5/month (100GB)
- **ECR Storage**: ~$3/month (20GB images)
- **Data Transfer**: ~$10/month
- **Total**: **~$151/month**

### Production Environment (Monthly)
- **EKS Cluster**: ~$73/month
- **EC2 Nodes**: ~$240/month (3x t3.xlarge)
- **RDS PostgreSQL**: ~$150/month (db.t3.medium)
- **S3 Storage**: ~$20/month (500GB)
- **ECR Storage**: ~$5/month
- **Data Transfer**: ~$50/month
- **Total**: **~$538/month**

---

## ⚠️ Known Issues & Limitations

### Current Limitations
1. **No GPU Support**: CPU-only PyTorch for cost efficiency (slower ML inference)
2. **Single Celery Worker**: Staging has 1 worker (production will have 2-8)
3. **Missing Features**: Birth certificate, voter's cert, liveness detection disabled
4. **No SSL Yet**: HTTP only (SSL will be configured during deployment)
5. **No Monitoring**: Prometheus/Grafana not yet configured

### Technical Debt
1. **Face Recognition**: Requires dlib/CMake (excluded from staging)
2. **Database Backups**: Need to configure automated backups
3. **Log Aggregation**: Need centralized logging (CloudWatch or ELK)
4. **CI/CD Pipeline**: GitHub Actions not yet configured

---

## 🎯 Deployment Checklist

### Pre-Deployment (Preparation Phase) ✅ COMPLETE
- [x] Docker images built and tested locally
- [x] Kubernetes manifests created
- [x] Secrets management strategy implemented
- [x] AWS infrastructure prepared (S3, ECR)
- [x] Resource allocations calculated
- [x] Documentation written
- [x] Cost estimates completed

### Deployment Phase (Not Started Yet)
- [ ] Push Docker images to ECR
- [ ] Install eksctl and kubectl
- [ ] Create EKS cluster
- [ ] Configure kubectl context
- [ ] Generate and apply K8s secrets
- [ ] Deploy all services to staging
- [ ] Run database migrations
- [ ] Create Django superuser
- [ ] Configure DNS/LoadBalancer
- [ ] Run integration tests
- [ ] Monitor logs and metrics
- [ ] Document any issues
- [ ] Get stakeholder approval

### Post-Deployment (Future)
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups
- [ ] Implement CI/CD pipeline
- [ ] Load testing and optimization
- [ ] Security audit
- [ ] User acceptance testing
- [ ] Production deployment

---

## 📞 Support & Maintenance

### Key Contacts
- **Development Team**: TCU-CEAA Dev Team
- **AWS Account**: 466901691218
- **Region**: us-east-1 (US East N. Virginia)

### Troubleshooting Resources
1. AWS_DEPLOYMENT_STEP_BY_STEP.md - Comprehensive troubleshooting
2. KUBERNETES_README.md - K8s command reference
3. Docker logs: `docker logs <container-id>`
4. K8s logs: `kubectl logs <pod-name> -n tcu-ceaa-staging`

### Useful Commands

#### Docker
```bash
# View all images
docker images

# Remove old images
docker image prune -a

# Check container logs
docker logs <container-id>
```

#### Kubernetes
```bash
# Get all pods
kubectl get pods -n tcu-ceaa-staging

# Describe pod (for troubleshooting)
kubectl describe pod <pod-name> -n tcu-ceaa-staging

# View logs
kubectl logs -f <pod-name> -n tcu-ceaa-staging

# Execute command in pod
kubectl exec -it <pod-name> -n tcu-ceaa-staging -- /bin/bash
```

#### AWS
```bash
# List ECR images
aws ecr list-images --repository-name tcu-ceaa/backend

# Get EKS cluster info
aws eks describe-cluster --name tcu-ceaa-staging

# List S3 buckets
aws s3 ls
```

---

## 🔄 Version History

### v1.0.0 - Preparation Phase Complete (November 12, 2025)
- ✅ Docker images built (backend, celery, frontend)
- ✅ CPU-only PyTorch implementation (4.46GB vs 14.4GB)
- ✅ Kubernetes manifests for staging and production
- ✅ AWS infrastructure prepared (S3, ECR)
- ✅ Secrets management system implemented
- ✅ Resource allocations optimized
- ✅ Comprehensive documentation written

### Next Release: v1.1.0 - Staging Deployment
- Deploy to AWS EKS staging environment
- Configure DNS and SSL
- Integration testing
- Performance benchmarking

---

## 📝 Notes

### Why CPU-Only PyTorch?
- **Cost Savings**: GPU instances are 3-5x more expensive
- **Sufficient for Staging**: CPU inference is fast enough for testing
- **Easy Upgrade Path**: Can switch to GPU instances later if needed
- **Image Size**: 70% smaller (4.46GB vs 14.4GB)

### Why No Face Recognition in Staging?
- **Complex Dependencies**: Requires CMake and dlib (difficult to build)
- **Feature Not Enabled**: Liveness detection is currently disabled
- **Future Implementation**: Will add when feature is ready for testing

### Why Two Dockerfiles?
- **Development** (`Dockerfile`): Hot reload, debugging, used by docker-compose
- **Production** (`Dockerfile.prod`): Optimized, security-hardened, multi-stage builds

---

## ✅ Sign-Off

**Prepared By**: AI Assistant  
**Reviewed By**: _Pending_  
**Approved By**: _Pending_  
**Date**: November 12, 2025  

**Status**: ✅ **Preparation Complete - Ready for Deployment Review**

---

*For deployment procedures, refer to `AWS_DEPLOYMENT_STEP_BY_STEP.md`*
