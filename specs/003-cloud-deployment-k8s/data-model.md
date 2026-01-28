# Data Model: Cloud Deployment & Production Readiness

**Feature**: 003-cloud-deployment-k8s
**Date**: 2026-01-21

This document defines Kubernetes resource specifications for the TaskFlow application deployment.

## Resource Overview

| Resource Type | Name | Purpose |
|---------------|------|---------|
| Deployment | taskflow-frontend | Next.js frontend application |
| Deployment | taskflow-backend | FastAPI backend API |
| Deployment | taskflow-mcp-server | MCP tool server for AI agent |
| Service | taskflow-frontend | Expose frontend internally |
| Service | taskflow-backend | Expose backend internally |
| Service | taskflow-mcp-server | Expose MCP server internally |
| Ingress | taskflow-ingress | External HTTP routing |
| ConfigMap | taskflow-config | Non-sensitive configuration |
| Secret | taskflow-secrets | Sensitive credentials |
| HPA | taskflow-backend-hpa | Backend autoscaling |

---

## Deployments

### Frontend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskflow-frontend
  labels:
    app: taskflow
    component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: taskflow
      component: frontend
  template:
    metadata:
      labels:
        app: taskflow
        component: frontend
    spec:
      containers:
        - name: frontend
          image: ghcr.io/USER/taskflow-frontend:TAG
          ports:
            - containerPort: 3000
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          env:
            - name: NEXT_PUBLIC_API_URL
              valueFrom:
                configMapKeyRef:
                  name: taskflow-config
                  key: API_URL
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /api/health?full=1
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskflow-backend
  labels:
    app: taskflow
    component: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: taskflow
      component: backend
  template:
    metadata:
      labels:
        app: taskflow
        component: backend
    spec:
      containers:
        - name: backend
          image: ghcr.io/USER/taskflow-backend:TAG
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: 200m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          envFrom:
            - configMapRef:
                name: taskflow-config
            - secretRef:
                name: taskflow-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health?full=1
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
```

### MCP Server Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskflow-mcp-server
  labels:
    app: taskflow
    component: mcp-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: taskflow
      component: mcp-server
  template:
    metadata:
      labels:
        app: taskflow
        component: mcp-server
    spec:
      containers:
        - name: mcp-server
          image: ghcr.io/USER/taskflow-mcp-server:TAG
          ports:
            - containerPort: 8001
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          envFrom:
            - configMapRef:
                name: taskflow-config
            - secretRef:
                name: taskflow-secrets
          livenessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 5
```

---

## Services

### Frontend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: taskflow-frontend
  labels:
    app: taskflow
    component: frontend
spec:
  type: ClusterIP
  selector:
    app: taskflow
    component: frontend
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
```

### Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: taskflow-backend
  labels:
    app: taskflow
    component: backend
spec:
  type: ClusterIP
  selector:
    app: taskflow
    component: backend
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP
```

### MCP Server Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: taskflow-mcp-server
  labels:
    app: taskflow
    component: mcp-server
spec:
  type: ClusterIP
  selector:
    app: taskflow
    component: mcp-server
  ports:
    - port: 8001
      targetPort: 8001
      protocol: TCP
```

---

## Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taskflow-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: taskflow-frontend
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: taskflow-backend
                port:
                  number: 8000
          - path: /mcp
            pathType: Prefix
            backend:
              service:
                name: taskflow-mcp-server
                port:
                  number: 8001
```

---

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: taskflow-config
data:
  # Frontend configuration
  API_URL: "http://taskflow-backend:8000"

  # Backend configuration
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "http://taskflow-frontend"

  # MCP Server configuration
  MCP_PORT: "8001"
```

---

## Secret Template

```yaml
# secrets.yaml.template - Copy to secrets.yaml and fill values
apiVersion: v1
kind: Secret
metadata:
  name: taskflow-secrets
type: Opaque
stringData:
  # Database credentials (Neon Serverless)
  DATABASE_URL: "postgresql://user:password@host/database"

  # Gemini API credentials
  GEMINI_API_KEY: "your-api-key"

  # JWT secrets
  JWT_SECRET_KEY: "your-jwt-secret"
  BETTER_AUTH_SECRET: "your-better-auth-secret"
```

---

## Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: taskflow-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: taskflow-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

---

## Resource Relationships

```
                    ┌─────────────────┐
                    │    Ingress      │
                    │  (HTTP routing) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Frontend Service │ │ Backend Service │ │ MCP Service     │
│   (ClusterIP)   │ │   (ClusterIP)   │ │   (ClusterIP)   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Frontend Deploy │ │ Backend Deploy  │ │ MCP Deploy      │
│  (2 replicas)   │ │  (2-10 replicas)│ │  (1 replica)    │
└─────────────────┘ └────────┬────────┘ └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      HPA        │
                    │ (autoscaling)   │
                    └─────────────────┘

All pods consume:
- ConfigMap: taskflow-config (non-sensitive env vars)
- Secret: taskflow-secrets (credentials)
```

---

## Environment Variables by Service

### Frontend

| Variable | Source | Description |
|----------|--------|-------------|
| NEXT_PUBLIC_API_URL | ConfigMap | Backend API URL |

### Backend

| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | Neon PostgreSQL connection string |
| GEMINI_API_KEY | Secret | Gemini API credentials |
| JWT_SECRET_KEY | Secret | JWT signing key |
| BETTER_AUTH_SECRET | Secret | BetterAuth secret |
| ENVIRONMENT | ConfigMap | Runtime environment |
| LOG_LEVEL | ConfigMap | Logging verbosity |
| CORS_ORIGINS | ConfigMap | Allowed CORS origins |

### MCP Server

| Variable | Source | Description |
|----------|--------|-------------|
| DATABASE_URL | Secret | Neon PostgreSQL connection string |
| MCP_PORT | ConfigMap | Server port |

---

## Validation Rules

1. **Image tags**: Must use git SHA, not `latest`
2. **Resource limits**: All containers must have limits defined
3. **Probes**: All containers must have liveness and readiness probes
4. **Secrets**: Never store in ConfigMaps; use Secrets with base64 encoding
5. **Labels**: All resources must have `app: taskflow` and `component` labels
