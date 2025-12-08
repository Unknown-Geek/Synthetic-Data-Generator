# Frontend Dockerfile for Synthetic Data Generator
# Multi-stage build: Node.js for build, nginx for serving

# Stage 1: Build the React app
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source files
COPY . .

# Set build-time environment variables
ARG REACT_APP_API_URL=http://localhost:7860
ARG REACT_APP_PRODUCTION_API_URL=http://backend:7860
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_PRODUCTION_API_URL=$REACT_APP_PRODUCTION_API_URL
ENV NODE_OPTIONS=--openssl-legacy-provider

# Build the app
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
