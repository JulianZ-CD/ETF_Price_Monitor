#!/bin/bash
# Build and push multi-platform Docker images (amd64 + arm64)

set -e

# Check buildx
if ! docker buildx version > /dev/null 2>&1; then
    echo "Error: docker buildx not available"
    exit 1
fi

# Create or use builder
if ! docker buildx inspect multiplatform > /dev/null 2>&1; then
    docker buildx create --name multiplatform --use
else
    docker buildx use multiplatform
fi

# Build and push backend
echo "Building backend..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --file Dockerfile.backend \
    --tag ghcr.io/julianz-cd/etf_price_monitor-backend:latest \
    --push \
    .

# Build and push frontend
echo "Building frontend..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --file Dockerfile.frontend \
    --tag ghcr.io/julianz-cd/etf_price_monitor-frontend:latest \
    --build-arg DOCKER_ENV=true \
    --build-arg DEPLOYMENT_MODE=multi \
    --push \
    .

echo "Done."

