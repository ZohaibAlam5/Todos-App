# TaskFlow Frontend Dockerfile
# Multi-stage build with development and production targets

# =============================================================================
# BASE STAGE - Common dependencies
# =============================================================================
FROM node:20-alpine AS base

# Install dependencies only when needed
RUN apk add --no-cache libc6-compat

WORKDIR /app

# =============================================================================
# DEPENDENCIES STAGE - Install node_modules
# =============================================================================
FROM base AS deps

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm ci

# =============================================================================
# DEVELOPMENT STAGE - For local development with hot-reload
# =============================================================================
FROM base AS development

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source files (will be overridden by volume mount in docker-compose)
COPY frontend/ .

# Set development environment
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Expose port
EXPOSE 3000

# Start development server with hot-reload
CMD ["npm", "run", "dev"]

# =============================================================================
# BUILDER STAGE - Build the production application
# =============================================================================
FROM base AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source files
COPY frontend/ .

# Set production environment for build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application with standalone output
RUN npm run build

# =============================================================================
# PRODUCTION STAGE - Minimal runtime image
# =============================================================================
FROM node:20-alpine AS production

WORKDIR /app

# Don't run as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Copy the standalone build
COPY --from=builder /app/public ./public

# Set the correct permissions for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone output (if available) or full build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

# Start the production server
CMD ["node", "server.js"]
