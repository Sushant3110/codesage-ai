# ==============================================================================
# CodeSage AI — Frontend Dockerfile
# Multi-stage production build for React + Vite + Tailwind CSS SPA
# ==============================================================================

# ── Stage 1: Build static assets ─────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy frontend source files
COPY . .

# Build-time environment variable for backend API URL
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build production bundle into /app/dist
RUN npm run build

# ── Stage 2: Serve via Nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runner

# Replace default nginx configuration with SPA-aware configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
