# Environment Variables Documentation

This document describes all environment variables used by the TaskFlow application.

## Overview

Variables are organized by service and sensitivity:
- **ConfigMap Variables**: Non-sensitive configuration, stored in Kubernetes ConfigMaps
- **Secret Variables**: Sensitive credentials, stored in Kubernetes Secrets

---

## Frontend Service

### ConfigMap Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Node.js environment | `production` | Yes |
| `NEXT_PUBLIC_API_URL` | Backend API URL for client-side requests | `http://taskflow-backend:8000` | Yes |
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry | `1` | No |

---

## Backend Service

### ConfigMap Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `production` | Yes |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `FRONTEND_URL` | Frontend URL for CORS | `http://taskflow-frontend` | Yes |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | - | Yes |
| `PORT` | Server port | `8000` | No |

### Secret Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string (Neon Serverless) | Yes |
| `SECRET_KEY` | JWT signing secret (min 256 bits) | Yes |
| `JWT_SECRET_KEY` | Alternative JWT secret key | No |
| `BETTER_AUTH_SECRET` | BetterAuth library secret | Yes |
| `GEMINI_API_KEY` | Google Gemini AI API key | Yes |
| `GEMINI_MODEL` | Gemini model to use | No |
| `BREVO_API_KEY` | Brevo (Sendinblue) email API key | No |
| `EMAIL_FROM` | Sender email address | No |

---

## MCP Server Service

### ConfigMap Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `production` | Yes |
| `MCP_PORT` | MCP server port | `8001` | No |
| `BACKEND_URL` | Backend API URL for tool execution | `http://taskflow-backend:8000` | Yes |

### Secret Variables

MCP Server uses the same secrets as Backend when executing authenticated tool calls.

---

## Kubernetes Configuration

### Development Environment

ConfigMap location: `k8s/overlays/development/configmap.yaml`

Development uses relaxed settings:
- `LOG_LEVEL=DEBUG`
- `CORS_ORIGINS=*`
- Single replica deployments

### Production Environment

ConfigMap location: `k8s/overlays/production/configmap.yaml`
Secrets template: `k8s/overlays/production/secrets.yaml.template`

Production uses strict settings:
- `LOG_LEVEL=INFO`
- Restricted CORS origins
- Multiple replica deployments
- Secrets from Kubernetes Secrets

---

## Docker Compose Configuration

For local development with Docker Compose:

1. Copy `.env.example` to `.env`
2. Fill in required values
3. Run `docker-compose up`

Variables are passed to containers via the `environment` section in `docker-compose.yml`.

---

## Security Notes

1. **Never commit secrets** to version control
2. **Use Kubernetes Secrets** for all sensitive data in production
3. **Rotate secrets** regularly, especially `SECRET_KEY` and API keys
4. **Restrict CORS origins** in production to your actual domain
5. **Use SSL/TLS** for database connections (`sslmode=require`)

---

## Generating Secrets

```bash
# Generate a secure random secret (256 bits)
openssl rand -hex 32

# Generate a base64-encoded secret for Kubernetes
echo -n "your-secret-value" | base64
```
