# TaskFlow Backend Dockerfile
# Multi-stage build with development and production targets

# =============================================================================
# BASE STAGE - Common Python setup
# =============================================================================
FROM python:3.11-slim AS base

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# DEPENDENCIES STAGE - Install Python packages
# =============================================================================
FROM base AS deps

# Copy requirements file
COPY backend/TaskFlow-App/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# DEVELOPMENT STAGE - For local development with auto-reload
# =============================================================================
FROM base AS development

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy source files (will be overridden by volume mount in docker-compose)
COPY backend/TaskFlow-App/ .

# Set development environment
ENV ENVIRONMENT=development
ENV PORT=8000

# Expose port
EXPOSE 8000

# Start development server with auto-reload
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# PRODUCTION STAGE - Optimized runtime image
# =============================================================================
FROM python:3.11-slim AS production

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV PORT=8000

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Copy source files
COPY --chown=appuser:appuser backend/TaskFlow-App/ .

EXPOSE 8000

# Start production server with gunicorn + uvicorn workers
CMD ["gunicorn", "app:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
