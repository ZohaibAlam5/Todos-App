# Quickstart: Cloud Deployment & Production Readiness

**Feature**: 003-cloud-deployment-k8s
**Date**: 2026-01-21

This guide covers local development with Docker Compose and Kubernetes deployment.

## Prerequisites

- Docker Desktop or Docker Engine with Docker Compose
- kubectl (Kubernetes CLI)
- kind (for local Kubernetes)
- GitHub account (for container registry)

## Local Development with Docker Compose

### 1. Start All Services

```bash
# Clone the repository
git clone https://github.com/USER/Todo.git
cd Todo

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Build and start all services
docker-compose up --build
```

### 2. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js web application |
| Backend | http://localhost:8000 | FastAPI API |
| Backend Docs | http://localhost:8000/docs | Swagger API documentation |
| MCP Server | http://localhost:8001 | MCP tool server |

### 3. Development Workflow

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Rebuild single service after changes
docker-compose build frontend
docker-compose up -d frontend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### 4. Hot Reload

- **Frontend**: Changes to `frontend/src/` are reflected immediately
- **Backend**: Changes to `backend/` trigger automatic Uvicorn reload

---

## Kubernetes Deployment (Local with kind)

### 1. Create Cluster

```bash
# Install kind (if not installed)
# macOS: brew install kind
# Windows: choco install kind

# Create cluster
kind create cluster --name taskflow

# Verify cluster
kubectl cluster-info --context kind-taskflow
```

### 2. Build and Load Images

```bash
# Build production images
docker build -f docker/frontend/Dockerfile -t taskflow-frontend:latest --target production .
docker build -f docker/backend/Dockerfile -t taskflow-backend:latest --target production .
docker build -f docker/mcp-server/Dockerfile -t taskflow-mcp-server:latest --target production .

# Load images into kind cluster
kind load docker-image taskflow-frontend:latest --name taskflow
kind load docker-image taskflow-backend:latest --name taskflow
kind load docker-image taskflow-mcp-server:latest --name taskflow
```

### 3. Deploy with Kustomize

```bash
# Create secrets (from template)
cp k8s/overlays/development/secrets.yaml.template k8s/overlays/development/secrets.yaml
# Edit secrets.yaml with your credentials

# Deploy development overlay
kubectl apply -k k8s/overlays/development

# Verify deployment
kubectl get pods -l app=taskflow
kubectl get services -l app=taskflow
```

### 4. Access Application

```bash
# Port forward to access locally
kubectl port-forward svc/taskflow-frontend 3000:80 &
kubectl port-forward svc/taskflow-backend 8000:8000 &

# Access frontend
open http://localhost:3000
```

### 5. Useful Commands

```bash
# View pod logs
kubectl logs -l app=taskflow,component=backend -f

# Shell into pod
kubectl exec -it deployment/taskflow-backend -- /bin/sh

# Check pod health
kubectl describe pod -l app=taskflow,component=backend

# Scale deployment
kubectl scale deployment/taskflow-backend --replicas=3

# Rollout status
kubectl rollout status deployment/taskflow-backend

# Rollback
kubectl rollout undo deployment/taskflow-backend
```

### 6. Cleanup

```bash
# Delete resources
kubectl delete -k k8s/overlays/development

# Delete cluster
kind delete cluster --name taskflow
```

---

## Production Deployment (Cloud)

### 1. Push Images to Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag images
export GIT_SHA=$(git rev-parse --short HEAD)
docker tag taskflow-frontend:latest ghcr.io/USER/taskflow-frontend:$GIT_SHA
docker tag taskflow-backend:latest ghcr.io/USER/taskflow-backend:$GIT_SHA
docker tag taskflow-mcp-server:latest ghcr.io/USER/taskflow-mcp-server:$GIT_SHA

# Push images
docker push ghcr.io/USER/taskflow-frontend:$GIT_SHA
docker push ghcr.io/USER/taskflow-backend:$GIT_SHA
docker push ghcr.io/USER/taskflow-mcp-server:$GIT_SHA
```

### 2. Configure Production Secrets

```bash
# Create secrets (from template)
cp k8s/overlays/production/secrets.yaml.template k8s/overlays/production/secrets.yaml
# Edit secrets.yaml with production credentials (never commit!)

# Apply secrets
kubectl apply -f k8s/overlays/production/secrets.yaml
```

### 3. Deploy Production

```bash
# Update image tags in kustomization.yaml
# Set production image tags to $GIT_SHA

# Deploy production overlay
kubectl apply -k k8s/overlays/production

# Verify deployment
kubectl get pods -l app=taskflow -n production
kubectl rollout status deployment/taskflow-backend -n production
```

### 4. Configure Ingress

```bash
# Install NGINX Ingress Controller (if not available)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Get ingress IP
kubectl get ingress taskflow-ingress
```

---

## Environment Variables

### Required for All Environments

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection | postgresql://... |
| GEMINI_API_KEY | Gemini API key | AIza... |
| JWT_SECRET_KEY | JWT signing secret | (generate random) |
| BETTER_AUTH_SECRET | BetterAuth secret | (generate random) |

### Development Only

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

### Production Only

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://taskflow-backend:8000 |
| ENVIRONMENT | Runtime environment | production |
| LOG_LEVEL | Logging verbosity | INFO |

---

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs -l app=taskflow,component=backend --previous

# Check events
kubectl describe pod -l app=taskflow,component=backend
```

### ImagePullBackOff

```bash
# Verify image exists
docker pull ghcr.io/USER/taskflow-backend:TAG

# Check image pull secret
kubectl get secret regcred -o yaml
```

### Health Check Failures

```bash
# Test health endpoint directly
kubectl exec deployment/taskflow-backend -- curl localhost:8000/health

# Check probe configuration
kubectl get deployment taskflow-backend -o yaml | grep -A 10 livenessProbe
```

### Database Connection Issues

```bash
# Test database from pod
kubectl exec deployment/taskflow-backend -- python -c "
import os
from sqlmodel import create_engine
engine = create_engine(os.environ['DATABASE_URL'])
print(engine.connect())
"
```
