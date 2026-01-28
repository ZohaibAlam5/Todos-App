# TaskFlow Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the TaskFlow application.

## Directory Structure

```
k8s/
├── base/                          # Base manifests (shared across environments)
│   ├── frontend-deployment.yaml   # Frontend deployment
│   ├── frontend-service.yaml      # Frontend ClusterIP service
│   ├── backend-deployment.yaml    # Backend deployment
│   ├── backend-service.yaml       # Backend ClusterIP service
│   ├── mcp-server-deployment.yaml # MCP server deployment
│   ├── mcp-server-service.yaml    # MCP server ClusterIP service
│   ├── ingress.yaml               # Ingress for external access
│   ├── hpa.yaml                   # Horizontal Pod Autoscaler
│   └── kustomization.yaml         # Kustomize base configuration
├── overlays/
│   ├── development/               # Development environment
│   │   ├── kustomization.yaml     # Development overlay
│   │   └── configmap.yaml         # Development ConfigMap
│   └── production/                # Production environment
│       ├── kustomization.yaml     # Production overlay
│       ├── configmap.yaml         # Production ConfigMap
│       └── secrets.yaml.template  # Secrets template (copy and fill)
└── README.md                      # This file
```

## Prerequisites

- `kubectl` installed and configured
- Kubernetes cluster (local: kind/minikube, cloud: GKE/EKS/AKS)
- Docker images built and pushed to registry
- NGINX Ingress Controller installed

## Quick Start

### Local Development with kind

1. **Create cluster:**
   ```bash
   kind create cluster --name taskflow
   ```

2. **Install NGINX Ingress:**
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
   ```

3. **Build and load images:**
   ```bash
   # Build images
   docker build -f docker/frontend/Dockerfile --target production -t taskflow-frontend:local .
   docker build -f docker/backend/Dockerfile --target production -t taskflow-backend:local .
   docker build -f docker/mcp-server/Dockerfile --target production -t taskflow-mcp-server:local .

   # Load into kind
   kind load docker-image taskflow-frontend:local --name taskflow
   kind load docker-image taskflow-backend:local --name taskflow
   kind load docker-image taskflow-mcp-server:local --name taskflow
   ```

4. **Deploy:**
   ```bash
   kubectl apply -k k8s/overlays/development
   ```

5. **Access the application:**
   ```bash
   kubectl port-forward svc/taskflow-frontend 3000:80 -n taskflow-dev
   # Open http://localhost:3000
   ```

### Production Deployment

1. **Create namespace:**
   ```bash
   kubectl create namespace taskflow-prod
   ```

2. **Create secrets:**
   ```bash
   cd k8s/overlays/production
   cp secrets.yaml.template secrets.yaml
   # Edit secrets.yaml with your actual values
   kubectl apply -f secrets.yaml -n taskflow-prod
   ```

3. **Update image tags in kustomization.yaml:**
   ```yaml
   images:
     - name: ghcr.io/OWNER/taskflow-frontend
       newTag: sha-YOUR_COMMIT_SHA
     - name: ghcr.io/OWNER/taskflow-backend
       newTag: sha-YOUR_COMMIT_SHA
     - name: ghcr.io/OWNER/taskflow-mcp-server
       newTag: sha-YOUR_COMMIT_SHA
   ```

4. **Deploy:**
   ```bash
   kubectl apply -k k8s/overlays/production
   ```

## Common Operations

### View pods and their status
```bash
kubectl get pods -l app=taskflow -n taskflow-dev
```

### View logs
```bash
kubectl logs -l component=backend -n taskflow-dev -f
```

### Scale deployment manually
```bash
kubectl scale deployment taskflow-backend --replicas=3 -n taskflow-dev
```

### Check HPA status
```bash
kubectl get hpa -n taskflow-dev
```

### Restart deployment (to pick up config changes)
```bash
kubectl rollout restart deployment/taskflow-backend -n taskflow-dev
```

### View events
```bash
kubectl get events -n taskflow-dev --sort-by='.lastTimestamp'
```

## Health Checks

All services expose health endpoints for Kubernetes probes:

| Service | Liveness | Readiness |
|---------|----------|-----------|
| Frontend | `/api/health` | `/api/health?full=1` |
| Backend | `/health` | `/health?full=1` |
| MCP Server | `/health` | `/health` |

## Troubleshooting

### Pods not starting

1. Check pod events: `kubectl describe pod <pod-name> -n <namespace>`
2. Check logs: `kubectl logs <pod-name> -n <namespace>`
3. Verify images are accessible: `kubectl get events -n <namespace>`

### Health check failures

1. Exec into pod: `kubectl exec -it <pod-name> -n <namespace> -- /bin/sh`
2. Test health endpoint: `curl localhost:<port>/health`

### Database connection issues

1. Verify DATABASE_URL in secrets
2. Check network policies
3. Test connectivity from pod: `kubectl exec -it <pod-name> -- curl <db-host>:<port>`

## Architecture

```
                    ┌─────────────────┐
                    │    Ingress      │
                    │  (NGINX)        │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │ /                 │ /api, /auth       │ /mcp
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Frontend        │ │ Backend         │ │ MCP Server      │
│ (Next.js)       │ │ (FastAPI)       │ │ (FastAPI)       │
│ 2 replicas      │ │ 2-10 replicas   │ │ 1 replica       │
└─────────────────┘ └────────┬────────┘ └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Neon PostgreSQL │
                    │ (External)      │
                    └─────────────────┘
```
