# Implementation Plan: Cloud Deployment & Production Readiness

**Branch**: `003-cloud-deployment-k8s` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-cloud-deployment-k8s/spec.md`

## Summary

Transform the TaskFlow Todo application from development-deployed services (Vercel frontend, Hugging Face backend) into a production-ready, containerized deployment using Docker and Kubernetes orchestration. This feature adds infrastructure-as-code artifacts without modifying application functionality.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend), YAML (Kubernetes/Docker)
**Primary Dependencies**: Docker, Kubernetes, Kustomize, GitHub Actions
**Storage**: N/A (infrastructure only - database remains Neon Serverless external)
**Testing**: Manual validation with minikube/kind, GitHub Actions CI verification
**Target Platform**: Kubernetes (local: minikube/kind, cloud: GKE/DigitalOcean)
**Project Type**: Infrastructure/DevOps (adds to existing web application)
**Performance Goals**: Pod startup <30s, health response <500ms, rolling update zero-downtime
**Constraints**: Cloud-agnostic manifests, no service mesh, database external
**Scale/Scope**: 3 containerized services, single cluster, 2-10 pod replicas per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-Driven Authority** | PASS | All infrastructure defined in spec.md |
| **Spec-First Development** | PASS | Spec completed before implementation plan |
| **Determinism & Reproducibility** | PASS | Container images tagged by SHA; manifests declarative |
| **Progressive Evolution** | PASS | Phase 4 builds on Phase 1-3; no breaking changes |
| **AI-Native Architecture** | PASS | MCP server containerized with same governance |
| **Constitutional Compliance** | PASS | All artifacts traceable to spec requirements |
| **Traceability** | PASS | FR-001 to FR-020 map to specific deliverables |
| **Error Handling Standards** | PASS | Health endpoints provide explicit status |
| **Security & Isolation** | PASS | Secrets management via K8s Secrets |
| **Development Stack** | PASS | Docker + Kubernetes per constitution |
| **Forbidden Actions** | PASS | No hardcoded secrets; all config via env vars |
| **Environment Configuration** | PASS | ConfigMaps/Secrets for all configuration |

**Gate Status**: PASS - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-cloud-deployment-k8s/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (K8s resource definitions)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (not applicable - no new APIs)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Existing application structure (unchanged)
backend/
├── TaskFlow-App/
│   └── app.py           # FastAPI application
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   ├── app/
│   └── services/
├── package.json
└── next.config.ts

# NEW: Infrastructure artifacts (this feature)
docker/
├── frontend/
│   └── Dockerfile       # Multi-stage: dev + production
├── backend/
│   └── Dockerfile       # Multi-stage: dev + production
└── mcp-server/
    └── Dockerfile       # Multi-stage: dev + production

k8s/
├── base/
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── mcp-server-deployment.yaml
│   ├── mcp-server-service.yaml
│   ├── ingress.yaml
│   └── kustomization.yaml
└── overlays/
    ├── development/
    │   ├── kustomization.yaml
    │   └── configmap.yaml
    └── production/
        ├── kustomization.yaml
        ├── configmap.yaml
        └── secrets.yaml.template

.github/
└── workflows/
    └── docker-build.yml  # CI/CD pipeline

docker-compose.yml            # Local development
docker-compose.override.yml   # Dev overrides (hot-reload)
```

**Structure Decision**: Infrastructure artifacts are added alongside existing application code. No modification to application source structure.

## Complexity Tracking

> No Constitution Check violations to justify.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Research Summary

See [research.md](./research.md) for full details.

### Key Decisions

1. **Container Registry**: GitHub Container Registry (ghcr.io)
   - Rationale: Integrated with GitHub, free tier, simple auth

2. **Local Kubernetes**: kind (Kubernetes in Docker)
   - Rationale: Lighter than minikube, CI-friendly, matches cloud behavior

3. **Configuration Management**: Kustomize
   - Rationale: Native kubectl support, no additional tools required

4. **Health Check Pattern**: Separate liveness and readiness probes
   - Rationale: Prevents traffic to unhealthy pods while allowing recovery time

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for Kubernetes resource definitions.

Key resources:
- 3 Deployments (frontend, backend, mcp-server)
- 3 Services (ClusterIP for internal, LoadBalancer/Ingress for external)
- 2 ConfigMaps (development, production)
- 1 Secret template (production credentials)
- 1 Ingress (external routing)
- 1 HPA (backend autoscaling)

### Contracts

No new API contracts - this feature is infrastructure-only. Existing backend APIs remain unchanged.

Health endpoints to add:
- `GET /health` (backend) - returns `{"status": "healthy", "database": "connected"}`
- `GET /api/health` (frontend) - returns `{"status": "healthy", "backend": "reachable"}`

### Quickstart

See [quickstart.md](./quickstart.md) for deployment instructions.
