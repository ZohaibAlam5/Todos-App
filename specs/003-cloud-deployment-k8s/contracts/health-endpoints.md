# Health Endpoint Contracts

**Feature**: 003-cloud-deployment-k8s
**Date**: 2026-01-21

This document defines the health check endpoint contracts for Kubernetes probes.

## Backend Health Endpoint

### Basic Health (Liveness Probe)

**Endpoint**: `GET /health`

**Purpose**: Verify the application process is running and responsive.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "taskflow-backend",
  "version": "1.0.0",
  "timestamp": "2026-01-21T10:00:00Z"
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "service": "taskflow-backend",
  "version": "1.0.0",
  "timestamp": "2026-01-21T10:00:00Z",
  "error": "Application not ready"
}
```

### Full Health (Readiness Probe)

**Endpoint**: `GET /health?full=1`

**Purpose**: Verify the application and all dependencies are ready to serve traffic.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "taskflow-backend",
  "version": "1.0.0",
  "timestamp": "2026-01-21T10:00:00Z",
  "checks": {
    "database": {
      "status": "connected",
      "latency_ms": 5
    },
    "gemini_api": {
      "status": "available"
    }
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "service": "taskflow-backend",
  "version": "1.0.0",
  "timestamp": "2026-01-21T10:00:00Z",
  "checks": {
    "database": {
      "status": "disconnected",
      "error": "Connection timeout"
    },
    "gemini_api": {
      "status": "available"
    }
  }
}
```

---

## Frontend Health Endpoint

### Basic Health (Liveness Probe)

**Endpoint**: `GET /api/health`

**Purpose**: Verify the Next.js server is running.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "taskflow-frontend",
  "timestamp": "2026-01-21T10:00:00Z"
}
```

### Full Health (Readiness Probe)

**Endpoint**: `GET /api/health?full=1`

**Purpose**: Verify the frontend can reach the backend.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "taskflow-frontend",
  "timestamp": "2026-01-21T10:00:00Z",
  "checks": {
    "backend": {
      "status": "reachable",
      "latency_ms": 15
    }
  }
}
```

**Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "service": "taskflow-frontend",
  "timestamp": "2026-01-21T10:00:00Z",
  "checks": {
    "backend": {
      "status": "unreachable",
      "error": "Connection refused"
    }
  }
}
```

---

## MCP Server Health Endpoint

### Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify the MCP server is running and tools are available.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "service": "taskflow-mcp-server",
  "timestamp": "2026-01-21T10:00:00Z",
  "tools": ["create_task", "list_tasks", "update_task", "delete_task", "complete_task"]
}
```

---

## Kubernetes Probe Configuration

### Liveness Probe (all services)
```yaml
livenessProbe:
  httpGet:
    path: /health  # or /api/health for frontend
    port: <service-port>
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Behavior**: If 3 consecutive failures, pod is restarted.

### Readiness Probe (all services)
```yaml
readinessProbe:
  httpGet:
    path: /health?full=1  # or /api/health?full=1 for frontend
    port: <service-port>
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
  successThreshold: 1
```

**Behavior**: If 2 consecutive failures, pod is removed from service endpoints.

---

## Implementation Notes

1. Health endpoints should be fast (<500ms response time)
2. Liveness checks should NOT include external dependencies
3. Readiness checks should verify critical dependencies
4. Health endpoints should NOT be authenticated
5. Health endpoints should NOT be exposed via public ingress
6. Version should be injected at build time via environment variable
