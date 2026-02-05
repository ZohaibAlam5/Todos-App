# syntax=docker.io/docker/dockerfile:1

# =============================================================================
# BASE STAGE
# =============================================================================
FROM node:20-slim AS base

WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# =============================================================================
# DEPENDENCIES STAGE
# =============================================================================
FROM base AS deps

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# =============================================================================
# DEVELOPMENT STAGE
# =============================================================================
FROM base AS development

ENV NODE_ENV=development

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

EXPOSE 3000

# IMPORTANT: Turbopack disabled
CMD ["npm", "run", "dev"]

# =============================================================================
# BUILDER STAGE
# =============================================================================
FROM base AS builder

ENV NODE_ENV=production

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

RUN npm run build

# =============================================================================
# PRODUCTION STAGE
# =============================================================================
FROM node:20-slim AS production

WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs \
 && adduser --system --uid 1001 nextjs

# Copy standalone output
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]