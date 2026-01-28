# TaskFlow Docker Configuration

This directory contains Dockerfiles for building TaskFlow service containers.

## Directory Structure

```
docker/
├── frontend/              # Frontend Dockerfile
│   └── Dockerfile         # Multi-stage build (development + production)
├── backend/               # Backend Dockerfile
│   └── Dockerfile         # Multi-stage build (development + production)
├── mcp-server/            # MCP Server Dockerfile
│   └── Dockerfile         # Multi-stage build (development + production)
└── README.md              # This file
```

## Build Targets

All Dockerfiles support two targets:

| Target | Purpose | Usage |
|--------|---------|-------|
| `development` | Local development with hot-reload | `docker-compose up` |
| `production` | Optimized for deployment | CI/CD, Kubernetes |

## Building Images

### Development (with docker-compose)

```bash
# Start all services with hot-reload
docker-compose up --build

# Start specific service
docker-compose up frontend --build
```

### Production (individual builds)

```bash
# Frontend
docker build -f docker/frontend/Dockerfile --target production -t taskflow-frontend:latest .

# Backend
docker build -f docker/backend/Dockerfile --target production -t taskflow-backend:latest .

# MCP Server
docker build -f docker/mcp-server/Dockerfile --target production -t taskflow-mcp-server:latest .
```

## Image Details

### Frontend (Next.js)

| Target | Base Image | Features |
|--------|------------|----------|
| development | node:20-alpine | Hot-reload enabled, full dependencies |
| production | node:20-alpine | Standalone output, minimal size |

**Exposed Port:** 3000

### Backend (FastAPI)

| Target | Base Image | Features |
|--------|------------|----------|
| development | python:3.11-slim | Uvicorn with reload |
| production | python:3.11-slim | Gunicorn with Uvicorn workers |

**Exposed Port:** 8000

### MCP Server (FastAPI)

| Target | Base Image | Features |
|--------|------------|----------|
| development | python:3.11-slim | Uvicorn with reload |
| production | python:3.11-slim | Gunicorn with Uvicorn workers |

**Exposed Port:** 8001

## Environment Variables

See [ENV_VARS.md](../specs/003-cloud-deployment-k8s/ENV_VARS.md) for complete documentation.
