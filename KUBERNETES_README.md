# TCU CEAA - Kubernetes Deployment Quick Start

## 🚀 Quick Deploy

### 1. Build Images
```bash
export REGISTRY="your-registry-url"
./scripts/build-images.sh v1.0.0
```

### 2. Update Secrets
Edit `k8s/01-secrets.yaml` with real credentials

### 3. Deploy
```bash
./scripts/deploy-k8s.sh
```

## 📁 File Structure

```
TCU_CEAA/
├── backend/
│   ├── Dockerfile.prod        # Production Django API
│   └── Dockerfile.celery      # Celery worker for ML tasks
├── frontend/
│   ├── Dockerfile.prod        # React app with Nginx
│   └── nginx.conf            # Nginx configuration
├── k8s/
│   ├── 00-namespace.yaml     # Kubernetes namespace
│   ├── 01-secrets.yaml       # Secrets & ConfigMap
│   ├── 02-postgres.yaml      # PostgreSQL StatefulSet
│   ├── 03-redis.yaml         # Redis Deployment
│   ├── 04-backend.yaml       # Django API Deployment
│   ├── 05-celery-worker.yaml # Celery worker Deployment
│   ├── 06-frontend.yaml      # React frontend Deployment
│   └── 07-ingress.yaml       # Ingress configuration
├── scripts/
│   ├── build-images.sh       # Build & push Docker images
│   └── deploy-k8s.sh         # Deploy to Kubernetes
├── docker-compose.prod.yml   # Local production testing
└── DEPLOYMENT_GUIDE.md       # Detailed guide
```

## 🔧 Local Testing

```bash
# Create .env file
cp .env.production .env
# Edit .env with your credentials

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

## 📊 Monitoring

```bash
# Check pods
kubectl get pods -n tcu-ceaa

# Check logs
kubectl logs -f deployment/backend -n tcu-ceaa
kubectl logs -f deployment/celery-worker -n tcu-ceaa

# Check services
kubectl get svc -n tcu-ceaa

# Check ingress
kubectl get ingress -n tcu-ceaa
```

## 🔄 Updates

```bash
# Build new version
./scripts/build-images.sh v1.0.1

# Rolling update
kubectl set image deployment/backend backend=YOUR_REGISTRY/tcu-ceaa-backend:v1.0.1 -n tcu-ceaa
kubectl set image deployment/celery-worker celery-worker=YOUR_REGISTRY/tcu-ceaa-celery:v1.0.1 -n tcu-ceaa
kubectl set image deployment/frontend frontend=YOUR_REGISTRY/tcu-ceaa-frontend:v1.0.1 -n tcu-ceaa
```

## 🛠️ Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n tcu-ceaa
kubectl logs <pod-name> -n tcu-ceaa
```

### Database issues
```bash
kubectl exec -it deployment/backend -n tcu-ceaa -- python manage.py dbshell
```

### Celery issues
```bash
kubectl exec -it deployment/celery-worker -n tcu-ceaa -- celery -A backend_project inspect active
```

## 📚 Full Documentation

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions.
