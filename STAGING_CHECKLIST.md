# 🚀 TCU CEAA - Staging Deployment Checklist

## ✅ Pre-Deployment (Do This First!)

### AWS Setup
- [ ] AWS account created/accessible
- [ ] Billing enabled
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS credentials configured: `aws configure`
- [ ] S3 bucket created: `tcu-ceaa-staging-media`
- [ ] Textract enabled (check AWS Console)

### Kubernetes Cluster
- [ ] Cluster created (EKS/GKE/AKS)
- [ ] kubectl installed: `kubectl version`
- [ ] kubectl configured: `kubectl cluster-info`
- [ ] Can access cluster: `kubectl get nodes`

### Container Registry
- [ ] Registry chosen (ECR/GCR/Docker Hub)
- [ ] Registry credentials configured
- [ ] Can login: `docker login <registry>`

### Secrets & Credentials
- [ ] Django SECRET_KEY generated
- [ ] PostgreSQL password generated
- [ ] AWS access keys ready
- [ ] Gmail app password created
- [ ] Updated `k8s/staging/01-secrets.yaml`

---

## 📦 Build & Push (Wednesday)

### Build Docker Images
```bash
export REGISTRY="your-registry-url"
cd d:/Python/TCU_CEAA

# Backend API
docker build -f backend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-backend:staging ./backend

# Celery Worker
docker build -f backend/Dockerfile.celery -t $REGISTRY/tcu-ceaa-celery:staging ./backend

# Frontend
docker build -f frontend/Dockerfile.prod -t $REGISTRY/tcu-ceaa-frontend:staging ./frontend
```

- [ ] Backend image built successfully
- [ ] Celery image built successfully
- [ ] Frontend image built successfully

### Push Images
```bash
docker push $REGISTRY/tcu-ceaa-backend:staging
docker push $REGISTRY/tcu-ceaa-celery:staging
docker push $REGISTRY/tcu-ceaa-frontend:staging
```

- [ ] Backend image pushed
- [ ] Celery image pushed
- [ ] Frontend image pushed

### Update Manifests
```powershell
# Windows PowerShell
$env:REGISTRY = "your-registry-url"
Get-ChildItem k8s/staging/*.yaml | ForEach-Object {
    (Get-Content $_) -replace 'YOUR_REGISTRY', $env:REGISTRY | Set-Content $_
}
```

- [ ] Registry URL updated in all YAML files
- [ ] Verified changes: `git diff k8s/staging/`

---

## 🚀 Deploy to Staging (Thursday)

### Deploy to Kubernetes
```bash
cd d:/Python/TCU_CEAA

# Option 1: Use script
chmod +x scripts/deploy-staging.sh
./scripts/deploy-staging.sh

# Option 2: Manual
kubectl apply -f k8s/staging/00-namespace.yaml
kubectl apply -f k8s/staging/01-secrets.yaml
kubectl apply -f k8s/staging/02-postgres.yaml
kubectl apply -f k8s/staging/03-redis.yaml
kubectl apply -f k8s/staging/04-backend.yaml
kubectl apply -f k8s/staging/05-celery-worker.yaml
kubectl apply -f k8s/staging/06-frontend.yaml
kubectl apply -f k8s/staging/07-ingress.yaml
```

- [ ] Namespace created
- [ ] Secrets applied
- [ ] PostgreSQL deployed
- [ ] Redis deployed
- [ ] Backend deployed
- [ ] Celery worker deployed
- [ ] Frontend deployed
- [ ] Ingress configured

### Verify Deployment
```bash
# Check all pods
kubectl get pods -n tcu-ceaa-staging

# Should see:
# - postgres-0 (Running)
# - redis-xxx (Running)
# - backend-xxx (2 pods Running)
# - celery-worker-xxx (Running)
# - frontend-xxx (Running)
```

- [ ] All pods in "Running" state
- [ ] No "CrashLoopBackOff" errors
- [ ] No "ImagePullBackOff" errors

### Check Services
```bash
kubectl get svc -n tcu-ceaa-staging

# Get frontend URL
kubectl get svc frontend-service -n tcu-ceaa-staging -o wide
```

- [ ] All services created
- [ ] LoadBalancer IP assigned
- [ ] Can access frontend URL

### Check Logs
```bash
# Backend logs
kubectl logs -f deployment/backend -n tcu-ceaa-staging

# Celery logs
kubectl logs -f deployment/celery-worker -n tcu-ceaa-staging

# Database logs
kubectl logs -f statefulset/postgres -n tcu-ceaa-staging
```

- [ ] Backend started successfully
- [ ] Migrations ran successfully
- [ ] No critical errors in logs
- [ ] Celery worker connected to Redis

---

## 🧪 Testing (Thursday/Friday)

### Create Superuser
```bash
# Get backend pod name
kubectl get pods -n tcu-ceaa-staging | grep backend

# Create superuser
kubectl exec -it <backend-pod-name> -n tcu-ceaa-staging -- python manage.py createsuperuser
```

- [ ] Superuser created
- [ ] Can login to admin: `http://<ip>/admin/`

### Test Student Flow
- [ ] Open frontend: `http://<LoadBalancer-IP>`
- [ ] Register new student account
- [ ] Receive verification email
- [ ] Verify email (click link)
- [ ] Login successfully
- [ ] Complete basic qualification
- [ ] Upload COE document (PDF/JPG)
- [ ] Upload ID document (JPG)
- [ ] Wait for AI verification (~30 seconds)
- [ ] Check document status (APPROVED/REJECTED)
- [ ] Submit grades
- [ ] Complete full application form
- [ ] Submit application
- [ ] Receive confirmation email

### Test Admin Flow
- [ ] Login to admin dashboard
- [ ] View student applications
- [ ] See AI verification results
- [ ] Check confidence scores
- [ ] Approve application
- [ ] Verify email sent to student

### Test AI Features
- [ ] COE verification works (YOLOv8 + Textract)
- [ ] ID verification works
- [ ] Confidence scores displayed
- [ ] Extracted data shown (name, ID, etc.)
- [ ] Celery tasks processing in background

---

## 🐛 Troubleshooting

### If Pods Not Starting
```bash
kubectl describe pod <pod-name> -n tcu-ceaa-staging
kubectl logs <pod-name> -n tcu-ceaa-staging
```

### If Database Issues
```bash
# Check PostgreSQL
kubectl exec -it statefulset/postgres -n tcu-ceaa-staging -- psql -U postgres -d tcu_ceaa_staging

# Run migrations manually
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- python manage.py migrate
```

### If Images Not Pulling
```bash
# Check events
kubectl get events -n tcu-ceaa-staging --sort-by='.lastTimestamp'

# Verify registry access
docker pull $REGISTRY/tcu-ceaa-backend:staging
```

### If Frontend Can't Reach Backend
```bash
# Test from frontend pod
kubectl exec -it deployment/frontend -n tcu-ceaa-staging -- wget -O- http://backend-service:8000/health/
```

---

## 📊 Success Criteria

Before declaring "STAGING READY":

- [ ] ✅ All 5 pod types running
- [ ] ✅ Frontend accessible via browser
- [ ] ✅ Backend /health/ returns 200
- [ ] ✅ Can register new user
- [ ] ✅ Email verification works
- [ ] ✅ Can upload COE document
- [ ] ✅ COE AI verification completes
- [ ] ✅ Can upload ID document
- [ ] ✅ ID AI verification completes
- [ ] ✅ Can submit grades
- [ ] ✅ Can complete full application
- [ ] ✅ Admin can review applications
- [ ] ✅ Email notifications working
- [ ] ✅ No critical errors in logs

---

## 🎉 Launch Announcement

Once everything works, announce to team:

```
🚀 TCU CEAA Staging Environment is LIVE!

Frontend: http://<your-loadbalancer-ip>
Admin: http://<your-loadbalancer-ip>/admin

Test Credentials:
Username: admin
Password: <your-admin-password>

Features Available:
✅ User registration & authentication
✅ Email verification
✅ COE document AI verification (89% accuracy)
✅ ID document AI verification (89% accuracy)
✅ Grade submission
✅ Full application submission
✅ Admin review dashboard

Known Limitations (Manual Review Required):
⚠️ Birth certificate verification
⚠️ Voter's certificate verification
⚠️ Liveness/face detection

Please test thoroughly and report any issues!

Staging will be available until <date> for testing.
```

---

## 💡 Quick Commands Reference

```bash
# Watch all pods
kubectl get pods -n tcu-ceaa-staging -w

# Stream logs
kubectl logs -f deployment/backend -n tcu-ceaa-staging

# Restart pod
kubectl delete pod <pod-name> -n tcu-ceaa-staging

# Scale up/down
kubectl scale deployment backend --replicas=3 -n tcu-ceaa-staging

# Get shell in pod
kubectl exec -it deployment/backend -n tcu-ceaa-staging -- /bin/bash

# Port forward (for testing)
kubectl port-forward svc/backend-service 8000:8000 -n tcu-ceaa-staging

# Delete everything (start over)
kubectl delete namespace tcu-ceaa-staging
```

---

## ⏱️ Timeline

**Wednesday**: Build & push images (2-3 hours)  
**Thursday**: Deploy & verify (3-4 hours)  
**Friday**: Test & launch (2-3 hours)  

**Total**: ~8-10 hours spread over 3 days

---

## 📞 Need Help?

If stuck:
1. Check logs first
2. Google the error message
3. Check K8s events
4. Restart the problematic pod
5. Ask for help with specific error messages

---

**Good luck! You got this! 🚀**
