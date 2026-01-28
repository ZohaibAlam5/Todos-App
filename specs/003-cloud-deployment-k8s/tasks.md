claude# Tasks: Cloud Deployment & Production Readiness

**Input**: Design documents from `/specs/003-cloud-deployment-k8s/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: No automated tests requested. Manual validation via docker-compose and kubectl commands.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Infrastructure artifacts:
- **Docker**: `docker/<service>/Dockerfile`
- **Kubernetes base**: `k8s/base/<resource>.yaml`
- **Kubernetes overlays**: `k8s/overlays/<env>/`
- **CI/CD**: `.github/workflows/`
- **Root config**: `docker-compose.yml`, `.env.example`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and base configuration files

- [X] T001 Create docker/ directory structure with frontend/, backend/, mcp-server/ subdirectories
- [X] T002 Create k8s/base/ directory for Kubernetes base manifests
- [X] T003 Create k8s/overlays/development/ directory for dev environment
- [X] T004 Create k8s/overlays/production/ directory for prod environment
- [X] T005 [P] Create .env.example with all required environment variables documented
- [X] T006 [P] Create .dockerignore files for frontend, backend, and mcp-server in docker/

**Checkpoint**: Directory structure ready for artifact creation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Health endpoints required by all Kubernetes deployments - MUST complete before any K8s manifests can be validated

**⚠️ CRITICAL**: Kubernetes probes require health endpoints. Without these, pods will fail health checks.

- [X] T007 Implement /health endpoint in backend/TaskFlow-App/app.py with liveness check (basic status)
- [X] T008 Implement /health?full=1 endpoint in backend/TaskFlow-App/app.py with readiness check (database connectivity)
- [X] T009 [P] Create frontend health API route in frontend/src/app/api/health/route.ts for liveness
- [X] T010 [P] Create frontend health API route with full=1 support for readiness (backend connectivity check)

**Checkpoint**: Health endpoints ready - container deployments can now use probes

---

## Phase 3: User Story 1 - Local Development with Containers (Priority: P1) 🎯 MVP

**Goal**: Developers can run entire stack locally with `docker-compose up`

**Independent Test**: Run `docker-compose up --build` and verify:
1. All three services start and are accessible
2. Frontend hot-reload works on code changes
3. Backend auto-reload works on code changes
4. Services can communicate with each other

### Implementation for User Story 1

- [X] T011 [P] [US1] Create multi-stage Dockerfile for frontend in docker/frontend/Dockerfile with development target
- [X] T012 [P] [US1] Create multi-stage Dockerfile for backend in docker/backend/Dockerfile with development target
- [X] T013 [P] [US1] Create multi-stage Dockerfile for mcp-server in docker/mcp-server/Dockerfile with development target
- [X] T014 [US1] Create docker-compose.yml at repository root with all three services
- [X] T015 [US1] Create docker-compose.override.yml with volume mounts for hot-reload
- [X] T016 [US1] Configure docker-compose networking for inter-service communication
- [X] T017 [US1] Test docker-compose up --build and verify all services start correctly
- [X] T018 [US1] Test frontend hot-reload by modifying a component
- [X] T019 [US1] Test backend hot-reload by modifying an endpoint

**Checkpoint**: Local development environment fully functional with containers

---

## Phase 4: User Story 2 - Production Container Builds (Priority: P1)

**Goal**: CI/CD can build production-optimized images for deployment

**Independent Test**: Run `docker build --target production` for each service and verify:
1. Images build successfully
2. Images run in production mode
3. Images are optimized (no dev dependencies)

### Implementation for User Story 2

- [X] T020 [P] [US2] Add production target to docker/frontend/Dockerfile with standalone Next.js output
- [X] T021 [P] [US2] Add production target to docker/backend/Dockerfile with gunicorn/uvicorn workers
- [X] T022 [P] [US2] Add production target to docker/mcp-server/Dockerfile with production settings
- [X] T023 [US2] Create GitHub Actions workflow in .github/workflows/docker-build.yml
- [X] T024 [US2] Configure matrix build for all three services in CI workflow
- [X] T025 [US2] Add git SHA tagging for container images in CI workflow
- [X] T026 [US2] Configure push to GitHub Container Registry (ghcr.io) in CI workflow
- [X] T027 [US2] Add build caching to CI workflow for faster rebuilds
- [X] T028 [US2] Test production build locally: docker build -f docker/frontend/Dockerfile --target production .
- [X] T029 [US2] Test production build locally: docker build -f docker/backend/Dockerfile --target production .
- [X] T030 [US2] Test production build locally: docker build -f docker/mcp-server/Dockerfile --target production .

**Checkpoint**: Production images build successfully and are ready for K8s deployment

---

## Phase 5: User Story 3 - Kubernetes Deployment (Priority: P1)

**Goal**: Application deploys to Kubernetes cluster with all services running

**Independent Test**: Run `kubectl apply -k k8s/overlays/development` and verify:
1. All pods reach Running status
2. Services are created
3. Application is accessible via port-forward

### Implementation for User Story 3

- [X] T031 [P] [US3] Create frontend-deployment.yaml in k8s/base/ per data-model.md spec
- [X] T032 [P] [US3] Create frontend-service.yaml in k8s/base/ with ClusterIP type
- [X] T033 [P] [US3] Create backend-deployment.yaml in k8s/base/ per data-model.md spec
- [X] T034 [P] [US3] Create backend-service.yaml in k8s/base/ with ClusterIP type
- [X] T035 [P] [US3] Create mcp-server-deployment.yaml in k8s/base/ per data-model.md spec
- [X] T036 [P] [US3] Create mcp-server-service.yaml in k8s/base/ with ClusterIP type
- [X] T037 [US3] Create ingress.yaml in k8s/base/ with path routing for frontend, backend, mcp
- [X] T038 [US3] Create kustomization.yaml in k8s/base/ listing all resources
- [X] T039 [US3] Create kustomization.yaml in k8s/overlays/development/ referencing base
- [ ] T040 [US3] Test deployment with kind: kind create cluster --name taskflow
- [ ] T041 [US3] Load images to kind: kind load docker-image <image> --name taskflow
- [ ] T042 [US3] Apply manifests: kubectl apply -k k8s/overlays/development
- [ ] T043 [US3] Verify pods running: kubectl get pods -l app=taskflow
- [ ] T044 [US3] Test port-forward access: kubectl port-forward svc/taskflow-frontend 3000:80

**Checkpoint**: Application runs on Kubernetes with all services healthy

---

## Phase 6: User Story 4 - Environment Configuration (Priority: P2)

**Goal**: Configuration via ConfigMaps and Secrets without image changes

**Independent Test**: Deploy with different ConfigMap values and verify application uses them

### Implementation for User Story 4

- [X] T045 [P] [US4] Create configmap.yaml in k8s/overlays/development/ with development settings
- [X] T046 [P] [US4] Create configmap.yaml in k8s/overlays/production/ with production settings
- [X] T047 [US4] Create secrets.yaml.template in k8s/overlays/production/ with placeholder values
- [X] T048 [US4] Add .gitignore entry for k8s/overlays/production/secrets.yaml
- [X] T049 [US4] Update frontend deployment to use envFrom configMapRef
- [X] T050 [US4] Update backend deployment to use envFrom configMapRef and secretRef
- [X] T051 [US4] Update mcp-server deployment to use envFrom configMapRef and secretRef
- [X] T052 [US4] Document all environment variables in specs/003-cloud-deployment-k8s/ENV_VARS.md
- [ ] T053 [US4] Test config change: update ConfigMap, restart deployment, verify new value

**Checkpoint**: Environment configuration fully externalized from images

---

## Phase 7: User Story 5 - Health Monitoring and Self-Healing (Priority: P2)

**Goal**: Kubernetes automatically restarts unhealthy pods

**Independent Test**: Cause a pod to fail health check and verify Kubernetes restarts it

### Implementation for User Story 5

- [X] T054 [P] [US5] Configure liveness probe in frontend deployment with /api/health
- [X] T055 [P] [US5] Configure readiness probe in frontend deployment with /api/health?full=1
- [X] T056 [P] [US5] Configure liveness probe in backend deployment with /health
- [X] T057 [P] [US5] Configure readiness probe in backend deployment with /health?full=1
- [X] T058 [P] [US5] Configure liveness probe in mcp-server deployment with /health
- [X] T059 [P] [US5] Configure readiness probe in mcp-server deployment with /health
- [X] T060 [US5] Tune probe parameters: initialDelaySeconds, periodSeconds, timeoutSeconds, failureThreshold
- [ ] T061 [US5] Test liveness: exec into pod, kill process, verify restart
- [ ] T062 [US5] Test readiness: disconnect backend from database, verify traffic routing stops

**Checkpoint**: Self-healing operational - unhealthy pods are automatically restarted

---

## Phase 8: User Story 6 - Horizontal Scaling (Priority: P3)

**Goal**: Backend automatically scales based on load

**Independent Test**: Generate load and observe HPA creating additional pods

### Implementation for User Story 6

- [X] T063 [US6] Create hpa.yaml in k8s/base/ for backend autoscaling per data-model.md
- [X] T064 [US6] Add hpa.yaml to k8s/base/kustomization.yaml resources list
- [ ] T065 [US6] Configure metrics server in kind cluster (required for HPA)
- [ ] T066 [US6] Test HPA: kubectl get hpa taskflow-backend-hpa
- [ ] T067 [US6] Load test with hey or ab to trigger scale-up
- [ ] T068 [US6] Verify scale-down after load decreases

**Checkpoint**: Auto-scaling operational - backend scales with demand

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [X] T069 [P] Update quickstart.md with tested commands and troubleshooting
- [X] T070 [P] Create k8s/README.md with deployment instructions
- [X] T071 [P] Create docker/README.md with build instructions
- [ ] T072 Update main README.md with links to deployment documentation
- [X] T073 Run full validation: fresh clone → docker-compose up → all services work
- [ ] T074 Run K8s validation: fresh cluster → apply manifests → all pods healthy
- [X] T075 Verify no hardcoded secrets in any Dockerfile or manifest

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all Kubernetes deployments
- **US1 Local Dev (Phase 3)**: Depends on Phase 1 only (Dockerfiles don't need health endpoints)
- **US2 Production Builds (Phase 4)**: Depends on US1 Dockerfiles
- **US3 K8s Deployment (Phase 5)**: Depends on Phase 2 (health endpoints) and US2 (production images)
- **US4 Configuration (Phase 6)**: Depends on US3 (deployments must exist)
- **US5 Health Monitoring (Phase 7)**: Depends on Phase 2 (health endpoints) and US3
- **US6 Scaling (Phase 8)**: Depends on US3 and US5
- **Polish (Phase 9)**: Depends on all user stories

### User Story Dependencies

```
Phase 1 (Setup)
     │
     ├──────────────────────────────────────┐
     │                                      │
     ▼                                      ▼
Phase 2 (Health Endpoints)          Phase 3 (US1: Docker Compose)
     │                                      │
     │                                      ▼
     │                              Phase 4 (US2: Production Builds)
     │                                      │
     └───────────────────┬──────────────────┘
                         │
                         ▼
                 Phase 5 (US3: K8s Deployment)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               │
Phase 6 (US4)    Phase 7 (US5)           │
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                 Phase 8 (US6: HPA)
                         │
                         ▼
                 Phase 9 (Polish)
```

### Parallel Opportunities

**Phase 1** (all in parallel):
- T001-T006 can all run simultaneously

**Phase 2** (partially parallel):
- T007-T008 (backend health) in sequence
- T009-T010 (frontend health) can run parallel to backend

**Phase 3 - US1** (partially parallel):
- T011, T012, T013 (Dockerfiles) in parallel
- T014-T016 (docker-compose) in sequence after Dockerfiles

**Phase 4 - US2** (partially parallel):
- T020, T021, T022 (production targets) in parallel
- T023-T027 (CI workflow) in sequence
- T028, T029, T030 (local tests) in parallel

**Phase 5 - US3** (partially parallel):
- T031-T036 (deployments/services) all in parallel
- T037-T039 (ingress, kustomization) in sequence
- T040-T044 (testing) in sequence

---

## Parallel Example: Phase 5 - Kubernetes Manifests

```bash
# Launch all deployments and services in parallel:
Task: "Create frontend-deployment.yaml in k8s/base/"
Task: "Create frontend-service.yaml in k8s/base/"
Task: "Create backend-deployment.yaml in k8s/base/"
Task: "Create backend-service.yaml in k8s/base/"
Task: "Create mcp-server-deployment.yaml in k8s/base/"
Task: "Create mcp-server-service.yaml in k8s/base/"

# Then sequentially:
Task: "Create ingress.yaml in k8s/base/"
Task: "Create kustomization.yaml in k8s/base/"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Health endpoints (blocks K8s)
3. Complete Phase 3: US1 - Local Docker development ✓
4. Complete Phase 4: US2 - Production builds ✓
5. Complete Phase 5: US3 - K8s deployment ✓
6. **STOP and VALIDATE**: Application runs on Kubernetes
7. Deploy to cloud cluster (GKE/DigitalOcean)

### Incremental Delivery

1. Setup + Foundational → Health endpoints ready
2. Add US1 → Local dev works → Demo: `docker-compose up`
3. Add US2 → CI builds images → Demo: GitHub Actions
4. Add US3 → K8s deployment → Demo: `kubectl apply`
5. Add US4 → Config externalized → Demo: ConfigMap changes
6. Add US5 → Self-healing → Demo: Pod restart on failure
7. Add US6 → Auto-scaling → Demo: Load test scales pods

### Suggested MVP Scope

**Minimum Viable Deployment**: Complete through User Story 3 (Phase 5)

This delivers:
- ✅ Local development with Docker Compose
- ✅ Production container builds
- ✅ Kubernetes deployment with all services running
- ✅ Basic health checks (required for K8s)

Remaining stories (US4-US6) add operational maturity but aren't required for initial deployment.

---

## Task Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| 1 | Setup | 6 | 2 |
| 2 | Foundational | 4 | 2 |
| 3 | US1 (P1) | 9 | 3 |
| 4 | US2 (P1) | 11 | 5 |
| 5 | US3 (P1) | 14 | 6 |
| 6 | US4 (P2) | 9 | 2 |
| 7 | US5 (P2) | 9 | 6 |
| 8 | US6 (P3) | 6 | 0 |
| 9 | Polish | 7 | 3 |
| **Total** | | **75** | **29** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All Kubernetes manifests follow data-model.md specifications
- All Dockerfiles follow research.md patterns
