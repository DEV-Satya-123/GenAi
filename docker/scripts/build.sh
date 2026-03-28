#!/bin/bash

# Build script for AI Git Automation Agent
set -e

echo "🐳 Building AI Git Automation Agent Docker Images..."

# Build all services
echo "📦 Building backend..."
docker-compose build backend

echo "📦 Building frontend..."
docker-compose build frontend

echo "📦 Building nginx..."
docker-compose build nginx

echo "✅ All images built successfully!"

# Show image sizes
echo "📊 Image sizes:"
docker images | grep -E "(ai_git_agent|nginx|node|python)"

echo "🚀 Ready to deploy with: docker-compose up -d"