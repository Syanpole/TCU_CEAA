#!/bin/bash

# TCU CEAA - Deploy to Kubernetes
# This script deploys the application to a Kubernetes cluster

set -e

NAMESPACE="tcu-ceaa"

echo "🚀 Deploying TCU CEAA to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check cluster connection
echo "📡 Checking cluster connection..."
kubectl cluster-info

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f k8s/00-namespace.yaml

# Apply secrets and config (you should customize these first!)
echo "🔐 Applying secrets and configuration..."
read -p "Have you updated the secrets in k8s/01-secrets.yaml? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⚠️  Please update k8s/01-secrets.yaml with your actual secrets before deploying!"
    exit 1
fi
kubectl apply -f k8s/01-secrets.yaml

# Deploy PostgreSQL
echo "🐘 Deploying PostgreSQL..."
kubectl apply -f k8s/02-postgres.yaml

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s

# Deploy Redis
echo "📮 Deploying Redis..."
kubectl apply -f k8s/03-redis.yaml

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=120s

# Deploy Backend
echo "🔧 Deploying Backend API..."
kubectl apply -f k8s/04-backend.yaml

# Wait for backend to be ready
echo "⏳ Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=300s

# Deploy Celery Workers
echo "🔨 Deploying Celery Workers..."
kubectl apply -f k8s/05-celery-worker.yaml

# Deploy Frontend
echo "🎨 Deploying Frontend..."
kubectl apply -f k8s/06-frontend.yaml

# Deploy Ingress
echo "🌐 Deploying Ingress..."
kubectl apply -f k8s/07-ingress.yaml

echo "
✅ Deployment completed!

Check status:
  kubectl get all -n ${NAMESPACE}

Check logs:
  kubectl logs -f deployment/backend -n ${NAMESPACE}
  kubectl logs -f deployment/celery-worker -n ${NAMESPACE}
  kubectl logs -f deployment/frontend -n ${NAMESPACE}

Get service URLs:
  kubectl get ingress -n ${NAMESPACE}
  kubectl get svc -n ${NAMESPACE}
"

# Show pod status
echo "📊 Current pod status:"
kubectl get pods -n ${NAMESPACE}
