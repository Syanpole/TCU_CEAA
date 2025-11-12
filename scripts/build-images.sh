#!/bin/bash

# TCU CEAA - Build and Push Docker Images
# This script builds and pushes all Docker images to your container registry

set -e

# Configuration
REGISTRY="YOUR_REGISTRY" # e.g., gcr.io/project-id, ECR URL, or Docker Hub username
VERSION="${1:-latest}"

echo "🏗️  Building TCU CEAA Docker Images..."
echo "Registry: $REGISTRY"
echo "Version: $VERSION"

# Build Backend Image
echo "📦 Building Backend API..."
docker build -f backend/Dockerfile.prod -t ${REGISTRY}/tcu-ceaa-backend:${VERSION} ./backend
docker tag ${REGISTRY}/tcu-ceaa-backend:${VERSION} ${REGISTRY}/tcu-ceaa-backend:latest

# Build Celery Worker Image
echo "📦 Building Celery Worker..."
docker build -f backend/Dockerfile.celery -t ${REGISTRY}/tcu-ceaa-celery:${VERSION} ./backend
docker tag ${REGISTRY}/tcu-ceaa-celery:${VERSION} ${REGISTRY}/tcu-ceaa-celery:latest

# Build Frontend Image
echo "📦 Building Frontend..."
docker build -f frontend/Dockerfile.prod -t ${REGISTRY}/tcu-ceaa-frontend:${VERSION} ./frontend
docker tag ${REGISTRY}/tcu-ceaa-frontend:${VERSION} ${REGISTRY}/tcu-ceaa-frontend:latest

echo "✅ Build completed!"

# Push images
read -p "Push images to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🚀 Pushing images to registry..."
    
    docker push ${REGISTRY}/tcu-ceaa-backend:${VERSION}
    docker push ${REGISTRY}/tcu-ceaa-backend:latest
    
    docker push ${REGISTRY}/tcu-ceaa-celery:${VERSION}
    docker push ${REGISTRY}/tcu-ceaa-celery:latest
    
    docker push ${REGISTRY}/tcu-ceaa-frontend:${VERSION}
    docker push ${REGISTRY}/tcu-ceaa-frontend:latest
    
    echo "✅ Images pushed successfully!"
fi

echo "
🎉 Build complete!

Tagged images:
  - ${REGISTRY}/tcu-ceaa-backend:${VERSION}
  - ${REGISTRY}/tcu-ceaa-celery:${VERSION}
  - ${REGISTRY}/tcu-ceaa-frontend:${VERSION}

Next steps:
  1. Update k8s manifests with your registry URL
  2. Update secrets in k8s/01-secrets.yaml
  3. Deploy: kubectl apply -f k8s/
"
