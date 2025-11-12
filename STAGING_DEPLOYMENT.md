# TCU CEAA - Staging Deployment Guide

## 🎯 Quick Start - Deploy to Staging by Friday

### Prerequisites Checklist

- [ ] AWS Account with billing enabled
- [ ] Kubernetes cluster ready (EKS, GKE, or AKS)
- [ ] Docker installed locally
- [ ] kubectl configured and connected to cluster
- [ ] Domain/subdomain for staging (optional)

---

## 📋 Day-by-Day Plan

### **Wednesday (Today) - 4 hours**

#### 1. Set Up AWS Services (1 hour)

```bash
# Create S3 bucket for staging media
aws s3 mb s3://tcu-ceaa-staging-media --region us-east-1

# Enable Textract API (already enabled in most regions)
# No additional setup needed - just ensure AWS credentials work
```

#### 2. Generate Secrets (15 minutes)

```bash
# Generate Django SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generate PostgreSQL password
openssl rand -base64 32

# Get Gmail App Password
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Generate new app password for "Mail"
# 3. Copy the 16-character password
```

#### 3. Update Secrets File (15 minutes)

Edit `k8s/staging/01-secrets.yaml`:
```yaml
POSTGRES_PASSWORD: "paste-generated-password-here"
SECRET_KEY: "paste-django-secret-key-here"
AWS_ACCESS_KEY_ID: "your-aws-key"
AWS_SECRET_ACCESS_KEY: "your-aws-secret"
EMAIL_HOST_USER: "your-email@gmail.com"
EMAIL_HOST_PASSWORD: "your-16-char-app-password"
```

#### 4. Build Docker Images (1 hour)

```bash
# Set your registry (AWS ECR, GCR, Docker Hub, etc.)
export REGISTRY="123456789.dkr.ecr.us-east-1.amazonaws.com"

# Login to registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REGISTRY

# Build images
docker build -f backend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-backend:staging ./backend
docker build -f backend/Dockerfile.celery -t $REGISTRY/tcu-ceaa-celery:staging ./backend
docker build -f frontend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-frontend:staging ./frontend

# Push images
docker push $REGISTRY/tcu-ceaa-backend:staging
docker push $REGISTRY/tcu-ceaa-celery:staging
docker push $REGISTRY/tcu-ceaa-frontend:staging
```

#### 5. Update K8s Manifests (15 minutes)

Replace `YOUR_REGISTRY` in all staging YAML files:
```bash
# Linux/Mac
sed -i 's|YOUR_REGISTRY|'$REGISTRY'|g' k8s/staging/*.yaml

# Windows PowerShell
$env:REGISTRY = "your-registry-url"
Get-ChildItem k8s/staging/*.yaml | ForEach-Object {
    (Get-Content $_) -replace 'YOUR_REGISTRY', $env:REGISTRY | Set-Content $_
}
```

#### 6. Test Locally (1 hour)

```bash
# Test with docker-compose first
docker-compose -f docker-compose.prod.yml up

# Access at:
# Frontend: http://localhost
# Backend: http://localhost:8000

# Check logs for any errors
docker-compose -f docker-compose.prod.yml logs

# Stop when done
docker-compose -f docker-compose.prod.yml down
```

---

### **Thursday - 4 hours**

#### 7. Deploy to Kubernetes (1 hour)

```bash
# Connect to your cluster
kubectl config use-context your-staging-cluster

# Deploy
chmod +x scripts/deploy-staging.sh
./scripts/deploy-staging.sh

# Or manually:
kubectl apply -f k8s/staging/
```

#### 8. Verify Deployment (30 minutes)

```bash
# Check all pods are running
kubectl get pods -n tcu-ceaa-staging

# Check services
kubectl get svc -n tcu-ceaa-staging

# Get frontend URL
kubectl get svc frontend-service -n tcu-ceaa-staging

# Check logs
kubectl logs -f deployment/backend -n tcu-ceaa-staging
kubectl logs -f deployment/celery-worker -n tcu-ceaa-staging
```

#### 9. Create Superuser (15 minutes)

```bash
# Get backend pod name
kubectl get pods -n tcu-ceaa-staging

# Create Django superuser
kubectl exec -it <backend-pod-name> -n tcu-ceaa-staging -- python manage.py createsuperuser

# Access admin at: http://<your-ip>/admin/
```

#### 10. Test Complete Flow (2 hours)

**Student Flow:**
1. Register new student account
2. Verify email
3. Complete basic qualification
4. Upload COE document
5. Upload ID document
6. Submit grades
7. Complete full application

**Admin Flow:**
1. Login to admin dashboard
2. Review student applications
3. Approve/reject documents
4. Check AI verification results

---

### **Friday - 2 hours**

#### 11. Final Testing (1 hour)

```bash
# Test with 3-5 users
# - Registration
# - Document upload
# - Application submission
# - Email notifications
# - Admin review

# Load test (optional)
# kubectl run -it --rm load-test --image=busybox --restart=Never -- /bin/sh
# while true; do wget -q -O- http://frontend-service; done
```

#### 12. Documentation (30 minutes)

Create a simple guide for testers:
- Staging URL
- Test credentials
- Known limitations
- How to report bugs

#### 13. Announce Staging Launch (30 minutes)

Send to team:
```
🎉 TCU CEAA Staging Environment is Live!

Frontend: http://staging.tcu-ceaa.com
Admin: http://staging.tcu-ceaa.com/admin

Test Accounts:
- Student: test@tcu.edu / password123
- Admin: admin@tcu.edu / adminpass

Features Available:
✅ User registration & authentication
✅ COE document verification (AI-powered)
✅ ID verification (AI-powered)
✅ Grade submission
✅ Full application submission
✅ Admin review dashboard

Known Limitations:
⚠️ Birth certificate - manual review
⚠️ Voter's certificate - manual review
⚠️ Liveness detection - not implemented

Please test and report any issues!
```

---

## 🔧 Common Issues & Solutions

### Issue: Pods not starting
```bash
kubectl describe pod <pod-name> -n tcu-ceaa-staging
kubectl logs <pod-name> -n tcu-ceaa-staging
```

### Issue: Database connection failed
```bash
# Check PostgreSQL is running
kubectl get pods -l app=postgres -n tcu-ceaa-staging

# Check database logs
kubectl logs -l app=postgres -n tcu-ceaa-staging

# Test connection from backend
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- python manage.py dbshell
```

### Issue: Images not pulling
```bash
# Check image exists in registry
docker images | grep tcu-ceaa

# Verify registry credentials
kubectl get secret -n tcu-ceaa-staging

# Create pull secret if needed
kubectl create secret docker-registry regcred \
  --docker-server=$REGISTRY \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password) \
  -n tcu-ceaa-staging
```

### Issue: Frontend can't reach backend
```bash
# Check backend service
kubectl get svc backend-service -n tcu-ceaa-staging

# Check backend health endpoint
kubectl exec -it deployment/frontend -n tcu-ceaa-staging -- wget -O- http://backend-service:8000/health/
```

---

## 📊 Monitoring Staging

### View Logs
```bash
# All backend logs
kubectl logs -f deployment/backend -n tcu-ceaa-staging

# All celery logs
kubectl logs -f deployment/celery-worker -n tcu-ceaa-staging

# Database logs
kubectl logs -f statefulset/postgres -n tcu-ceaa-staging
```

### Check Resources
```bash
# Pod resource usage
kubectl top pods -n tcu-ceaa-staging

# Node resource usage
kubectl top nodes
```

### Scale if Needed
```bash
# Scale backend
kubectl scale deployment backend --replicas=3 -n tcu-ceaa-staging

# Scale celery workers
kubectl scale deployment celery-worker --replicas=2 -n tcu-ceaa-staging
```

---

## 💰 Cost Estimates (Staging)

### AWS EKS Staging
- **Cluster**: ~$73/month
- **2x t3.medium nodes**: ~$60/month
- **RDS db.t3.micro**: ~$15/month (optional)
- **S3 Storage**: ~$5/month
- **Textract**: Pay per page (~$1.50/1000 pages)
- **Total**: ~$150-200/month

### Cheaper Alternatives
- **Railway.app**: Free tier (500 hours)
- **Render.com**: Free tier for web services
- **Heroku**: Free tier (limited hours)

---

## 🎯 Success Criteria

Before declaring staging ready:

- [ ] All pods running (no CrashLoopBackOff)
- [ ] Frontend accessible via LoadBalancer IP
- [ ] Backend /health/ endpoint returns 200
- [ ] Database migrations completed
- [ ] Can register new user
- [ ] Can upload COE document
- [ ] AI verification works (COE & ID)
- [ ] Can submit full application
- [ ] Admin can review applications
- [ ] Email notifications working

---

## 🚀 Next Steps After Staging

1. **Week 1-2**: Gather feedback, fix bugs
2. **Week 3**: Implement birth cert detection
3. **Week 4**: Implement voter's cert detection
4. **Week 5**: Implement liveness detection
5. **Week 6**: Production deployment preparation
6. **Week 7**: Go live on production!

---

## 📞 Need Help?

If you encounter issues:
1. Check logs: `kubectl logs -f deployment/backend -n tcu-ceaa-staging`
2. Check pod status: `kubectl describe pod <pod-name> -n tcu-ceaa-staging`
3. Restart pod: `kubectl delete pod <pod-name> -n tcu-ceaa-staging`
4. Scale down/up: `kubectl scale deployment backend --replicas=0 -n tcu-ceaa-staging`

---

Good luck with your staging deployment! 🎉
