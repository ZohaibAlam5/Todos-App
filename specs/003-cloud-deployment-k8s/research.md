# Research: Cloud Deployment & Production Readiness

**Feature**: 003-cloud-deployment-k8s
**Date**: 2026-01-21

## Research Tasks

### 1. Container Registry Selection

**Question**: Which container registry should be used for storing Docker images?

**Options Evaluated**:
| Registry | Pros | Cons |
|----------|------|------|
| Docker Hub | Most widely used, easy setup | Rate limits on free tier, public by default |
| GitHub Container Registry (ghcr.io) | Integrated with GitHub, free private images | Less ecosystem support than Docker Hub |
| Google Container Registry (GCR) | GKE integration | Requires GCP account, cost for storage |
| Amazon ECR | EKS integration | Requires AWS account, complex IAM |

**Decision**: GitHub Container Registry (ghcr.io)

**Rationale**:
- Project already uses GitHub for source control
- Free tier includes private images
- Authentication uses existing GitHub tokens
- Seamless integration with GitHub Actions
- No rate limits for authenticated pulls

---

### 2. Local Kubernetes Environment

**Question**: Which tool should be used for local Kubernetes development?

**Options Evaluated**:
| Tool | Pros | Cons |
|------|------|------|
| minikube | Mature, feature-rich, multiple drivers | Resource heavy, slow startup |
| kind | Lightweight, CI-friendly, Docker-based | Fewer features than minikube |
| k3d | Fast, lightweight k3s in Docker | Less standard, k3s differences |
| Docker Desktop | Built-in, easy setup | Resource heavy, licensing concerns |

**Decision**: kind (Kubernetes in Docker)

**Rationale**:
- Runs entirely in Docker (already required for this project)
- Fast cluster creation (<60 seconds)
- Matches cloud Kubernetes behavior closely
- Excellent for CI/CD pipelines
- Minimal resource footprint

---

### 3. Configuration Management Tool

**Question**: How should Kubernetes manifests be organized for multiple environments?

**Options Evaluated**:
| Tool | Pros | Cons |
|------|------|------|
| Kustomize | Native kubectl support, no install | Less powerful than Helm |
| Helm | Powerful templating, package management | Additional dependency, complexity |
| Plain YAML | Simple, no learning curve | Duplication, maintenance burden |
| Jsonnet | Programmable, DRY | Steep learning curve |

**Decision**: Kustomize

**Rationale**:
- Built into kubectl (no additional tools)
- Declarative overlays match our simple needs
- Base + overlays pattern perfect for dev/prod
- Easy to understand for developers new to K8s
- Sufficient for project scope (no need for Helm complexity)

---

### 4. Multi-Stage Dockerfile Pattern

**Question**: What is the best pattern for Dockerfiles supporting both development and production?

**Research Findings**:

For **Next.js frontend**:
- Use multi-stage builds with named targets
- Development stage: includes devDependencies, enables hot-reload via volume mount
- Production stage: standalone output, no devDependencies, distroless base

For **FastAPI backend**:
- Use multi-stage builds with named targets
- Development stage: includes dev tools (pytest, black), uvicorn with reload
- Production stage: gunicorn with uvicorn workers, no dev dependencies

**Decision**: Multi-stage Dockerfiles with named targets (`development`, `production`)

**Pattern**:
```dockerfile
# Base stage with common dependencies
FROM node:20-alpine AS base
...

# Development stage (used with docker-compose)
FROM base AS development
CMD ["npm", "run", "dev"]

# Build stage (production build)
FROM base AS builder
RUN npm run build

# Production stage (minimal runtime)
FROM node:20-alpine AS production
COPY --from=builder /app/.next/standalone ./
CMD ["node", "server.js"]
```

---

### 5. Health Check Strategy

**Question**: How should health checks be implemented for Kubernetes probes?

**Research Findings**:

Kubernetes uses three probe types:
1. **Startup Probe**: Runs once at startup; prevents premature liveness checks
2. **Liveness Probe**: Determines if container should be restarted
3. **Readiness Probe**: Determines if container should receive traffic

**Best Practices**:
- Liveness: Check if process is alive (fast, no external deps)
- Readiness: Check if dependencies are available (database, external services)
- Use separate endpoints or query parameters for different checks
- Timeout/threshold tuning based on service characteristics

**Decision**: Implement `/health` endpoint with query parameter for probe type

**Pattern**:
```
GET /health          → Basic health (liveness)
GET /health?full=1   → Full health with dependencies (readiness)
```

**Backend Health Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-21T10:00:00Z",
  "checks": {
    "database": "connected",
    "gemini_api": "available"
  }
}
```

---

### 6. Resource Limits Strategy

**Question**: What are appropriate resource requests and limits for each service?

**Research Findings**:

Based on similar applications and best practices:

| Service | Request CPU | Request Memory | Limit CPU | Limit Memory |
|---------|-------------|----------------|-----------|--------------|
| Frontend | 100m | 128Mi | 500m | 512Mi |
| Backend | 200m | 256Mi | 1000m | 1Gi |
| MCP Server | 100m | 128Mi | 500m | 512Mi |

**Rationale**:
- Frontend: Static serving is lightweight; memory for SSR
- Backend: Higher for API processing; memory for ML inference
- MCP Server: Similar to frontend; tool execution overhead

**Decision**: Use above values as defaults; tune based on monitoring

---

### 7. Ingress Controller Selection

**Question**: Which ingress controller should be used?

**Options Evaluated**:
| Controller | Pros | Cons |
|------------|------|------|
| NGINX Ingress | Most common, well-documented | Configuration can be complex |
| Traefik | Auto-discovery, modern | Less enterprise adoption |
| Cloud-native (GKE, EKS) | Managed, integrated | Cloud-specific |

**Decision**: NGINX Ingress Controller (or cloud-native if available)

**Rationale**:
- Most widely used and documented
- Works consistently across local and cloud
- Manifests remain cloud-agnostic
- Easy path matching and TLS termination

---

### 8. CI/CD Pipeline Design

**Question**: How should the GitHub Actions workflow be structured?

**Research Findings**:

Best practices for container CI/CD:
1. Build on push to main and PRs
2. Use build cache for faster rebuilds
3. Tag images with git SHA + branch
4. Separate build and deploy jobs
5. Use OIDC for cloud authentication (no long-lived secrets)

**Decision**: GitHub Actions with matrix builds

**Pattern**:
```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [frontend, backend, mcp-server]
    steps:
      - Build image with cache
      - Tag with SHA
      - Push to ghcr.io
      - Scan for vulnerabilities
```

---

## Unresolved Questions

All NEEDS CLARIFICATION items resolved. No blockers for Phase 1.

## References

- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Kustomize Documentation](https://kustomize.io/)
- [kind Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
