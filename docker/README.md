# 🐳 Docker Deployment Guide

## Quick Start

### 1. Prerequisites
- Docker and Docker Compose installed
- `.env` file with your `GEMINI_API_KEY`

### 2. Build and Deploy
```bash
# Make scripts executable
chmod +x docker/scripts/*.sh

# Build all images
./docker/scripts/build.sh

# Deploy the application
./docker/scripts/deploy.sh
```

### 3. Access the Application
- **Frontend:** http://localhost
- **API:** http://localhost/api
- **API Docs:** http://localhost/api/docs
- **WebSocket:** ws://localhost/ws

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Nginx    │    │  Frontend   │    │   Backend   │
│   (Proxy)   │◄──►│   (React)   │    │  (FastAPI)  │
│   Port 80   │    │  Port 5173  │    │  Port 8000  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Services

### 🌐 Nginx (Reverse Proxy)
- **Image:** `nginx:alpine`
- **Purpose:** Route traffic, serve static files, SSL termination
- **Ports:** 80, 443
- **Config:** `docker/nginx/nginx.conf`

### ⚛️ Frontend (React)
- **Image:** `node:20-slim`
- **Purpose:** Serve React application
- **Port:** 5173 (internal)
- **Build:** Multi-stage build for optimization

### 🐍 Backend (FastAPI)
- **Image:** `python:3.10-slim`
- **Purpose:** API server, AI processing, Git operations
- **Port:** 8000 (internal)
- **Features:** Security scanning, commit message generation

## Commands

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Production
```bash
# Deploy with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3
```

### Maintenance
```bash
# Update images
docker-compose pull
docker-compose up -d

# Clean up
docker system prune -a
docker volume prune
```

## Environment Variables

Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
NODE_ENV=production
PYTHONPATH=/app
```

## Volumes

- `./repositories:/app/repositories` - Git repositories
- `./cloned-repos:/app/cloned-repos` - Cloned repositories
- `./docker/nginx/nginx.conf:/etc/nginx/nginx.conf` - Nginx config

## Health Checks

All services include health checks:
- **Nginx:** HTTP request to `/health`
- **Frontend:** HTTP request to root
- **Backend:** HTTP request to `/`

## Security Features

- Non-root users in all containers
- Security headers in Nginx
- Rate limiting for API endpoints
- CORS configuration
- SSL/TLS support (configurable)

## Troubleshooting

### Service not starting
```bash
# Check logs
docker-compose logs service_name

# Check container status
docker-compose ps

# Restart service
docker-compose restart service_name
```

### Port conflicts
```bash
# Check what's using port 80
sudo lsof -i :80

# Use different ports
docker-compose up -d -p 8080:80
```

### Permission issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./repositories ./cloned-repos
```

## Performance Tuning

### Nginx
- Gzip compression enabled
- Static file caching
- Connection keep-alive
- Worker process optimization

### Backend
- Uvicorn with multiple workers
- Async request handling
- Connection pooling

### Frontend
- Production build optimization
- Asset compression
- CDN-ready static files

## Monitoring

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# With timestamps
docker-compose logs -f -t
```

### Metrics
```bash
# Container stats
docker stats

# Service health
curl http://localhost/health
curl http://localhost/api/
```

## Backup

### Data
```bash
# Backup repositories
tar -czf backup-repos.tar.gz repositories/ cloned-repos/

# Backup configuration
tar -czf backup-config.tar.gz .env docker/
```

### Database (if added)
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U user dbname > backup.sql
```