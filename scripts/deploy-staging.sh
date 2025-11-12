#!/bin/bash

# TCU CEAA - Deploy to Staging Environment
# This script deploys the application to a staging Kubernetes cluster

set -e

NAMESPACE="tcu-ceaa-staging"
REGISTRY="${REGISTRY:-YOUR_REGISTRY}"
VERSION="${VERSION:-staging}"

echo "🚀 Deploying TCU CEAA to STAGING..."
echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo "Namespace: $NAMESPACE"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check cluster connection
echo "📡 Checking cluster connection..."
kubectl cluster-info

# Create namespace
echo "📦 Creating staging namespace..."
kubectl apply -f k8s/staging/00-namespace.yaml

# Apply secrets and config
echo "🔐 Applying secrets and configuration..."
echo "⚠️  WARNING: Make sure you've updated k8s/staging/01-secrets.yaml with real credentials!"
read -p "Have you updated the secrets? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please update k8s/staging/01-secrets.yaml with your actual secrets before deploying!"
    exit 1
fi
kubectl apply -f k8s/staging/01-secrets.yaml

# Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
kubectl apply -f k8s/staging/02-postgres.yaml

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s || echo "Warning: PostgreSQL might still be starting up"

# Deploy Redis
echo "📮 Deploying Redis..."
kubectl apply -f k8s/staging/03-redis.yaml

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=120s || echo "Warning: Redis might still be starting up"

# Deploy Backend
echo "🔧 Deploying Backend API..."
kubectl apply -f k8s/staging/04-backend.yaml

# Wait for backend to be ready
echo "⏳ Waiting for Backend to be ready..."
sleep 30  # Give init container time to run migrations
kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=300s || echo "Warning: Backend might still be starting up"

# Deploy Celery Workers
echo "🔨 Deploying Celery Workers..."
kubectl apply -f k8s/staging/05-celery-worker.yaml

# Deploy Frontend
echo "🎨 Deploying Frontend..."
kubectl apply -f k8s/staging/06-frontend.yaml

# Deploy Ingress
echo "🌐 Deploying Ingress..."
kubectl apply -f k8s/staging/07-ingress.yaml

echo "
✅ STAGING Deployment completed!

Check status:
  kubectl get all -n ${NAMESPACE}

Check logs:
  kubectl logs -f deployment/backend -n ${NAMESPACE}
  kubectl logs -f deployment/celery-worker -n ${NAMESPACE}
  kubectl logs -f deployment/frontend -n ${NAMESPACE}

Get service URLs:
  kubectl get ingress -n ${NAMESPACE}
  kubectl get svc frontend-service -n ${NAMESPACE}

Access your staging environment:
  Frontend: http://staging.tcu-ceaa.com (or LoadBalancer IP)
  Backend API: http://staging-api.tcu-ceaa.com

Note: This is a STAGING environment with:
  - Reduced resources
  - 2 backend replicas
  - 1 celery worker
  - 1 frontend replica
  - No auto-scaling
  - HTTP only (no HTTPS)

📊 Current pod status:
"
kubectl get pods -n ${NAMESPACE}

echo "
🔍 To get the LoadBalancer IP:
kubectl get svc frontend-service -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

🎉 Happy testing on staging!
"
