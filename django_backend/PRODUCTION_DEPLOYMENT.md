# Production Deployment & Operations Guide

**Complete guide for deploying SmartLaundry to production with Docker, monitoring, and scaling**

---

## 📋 Pre-Deployment Checklist

### ✅ Infrastructure
- [ ] Server with 2GB+ RAM (4GB+ recommended)
- [ ] PostgreSQL 13+ database
- [ ] Redis 6+ cache
- [ ] Domain name with DNS configured
- [ ] SSL certificate ready or Let's Encrypt configured
- [ ] CDN configured for static/media files (optional)

### ✅ Code & Configuration
- [ ] All tests passing (`pytest`)
- [ ] All migrations applied (`python manage.py migrate`)
- [ ] No DEBUG mode in production
- [ ] Unique SECRET_KEY generated (50+ characters)
- [ ] ALLOWED_HOSTS configured
- [ ] .env.production created with all variables
- [ ] Credentials secured (no hardcoded passwords)

### ✅ Security
- [ ] SECURE_SSL_REDIRECT = True
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Password hashing configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers in place

---

## 🐳 Docker Deployment (Recommended)

### Step 1: Server Setup

```bash
# Connect to server
ssh root@your-server-ip

# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
usermod -aG docker $USER

# Create app directory
mkdir -p /opt/smartlaundry && cd /opt/smartlaundry
```

### Step 2: Clone Repository

```bash
# Clone smartlaundry repo
git clone https://github.com/your-org/smartlaundry.git .
git checkout main

# Set permissions
chown -R 1000:1000 .
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env

# Critical variables to update:
# - DEBUG=False
# - SECRET_KEY=your-very-long-random-secret-key
# - DB_PASSWORD=your-secure-password
# - REDIS_PASSWORD=your-secure-password (if using)
# - STRIPE_SECRET_KEY=sk_live_xxxxx
# - EMAIL_HOST_PASSWORD=your-app-password
# - ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# - SECURE_SSL_REDIRECT=True
```

### Step 4: Launch Services

```bash
# Build images (if not using prebuilt)
docker-compose build

# Start services (background)
docker-compose up -d

# Check service status
docker-compose ps

# Expected output:
# CONTAINER ID   IMAGE                    STATUS
# xxxxxxxxxx     smartlaundry_web         Up 2 minutes (healthy)
# xxxxxxxxxx     smartlaundry_postgres    Up 2 minutes (healthy)
# xxxxxxxxxx     smartlaundry_redis       Up 2 minutes (healthy)
# xxxxxxxxxx     smartlaundry_celery      Up 2 minutes
# xxxxxxxxxx     smartlaundry_nginx       Up 2 minutes (healthy)
```

### Step 5: Initialize Database

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create cache tables (if using database cache)
docker-compose exec web python manage.py createcachetable

# Load initial data (if provided)
docker-compose exec web python manage.py loaddata initial_data
```

### Step 6: SSL Certificate Setup

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate from Let's Encrypt
certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  -n --agree-tos --email your-email@example.com

# Certificate files will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem

# Update docker-compose.yml with certificate paths
# Then restart nginx:
docker-compose restart nginx
```

### Step 7: Verification

```bash
# Check API health
curl https://your-domain.com/api/health/

# Check admin interface
# Visit: https://your-domain.com/admin/

# Check WebSocket (use WebSocket client)
# Connect to: wss://your-domain.com/ws/location/1/

# View logs
docker-compose logs -f web

# Check database
docker-compose exec postgres psql -U smartlaundry -d smartlaundry -c "\dt"

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## 🔄 Continuous Deployment (GitHub Actions)

### Setup CI/CD

The `.github/workflows/ci-cd.yml` file is already configured. Configure secrets:

```bash
# In GitHub repository settings, add these secrets:
STAGING_SSH_KEY          # Private SSH key for staging server
STAGING_HOST             # Staging server IP/domain
PROD_SSH_KEY             # Private SSH key for production server
PROD_HOST                # Production server IP/domain
DOCKER_REGISTRY_TOKEN    # GitHub container registry token
```

### Deployment Flow

```
Push to main branch
    ↓
Run tests
    ↓
Run linting & security scans
    ↓
Build Docker image
    ↓
Push to registry
    ↓
Deploy to production
    ↓
Run health checks
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoint

```bash
# All services should respond to:
curl https://your-domain.com/api/health/

# Response:
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok",
  "celery": "ok"
}
```

### View Logs

```bash
# Django application logs
docker-compose logs -f web

# Celery worker logs
docker-compose logs -f celery_worker

# Nginx access logs
docker-compose logs -f nginx

# PostgreSQL logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### Monitor Resources

```bash
# Check container resource usage
docker stats

# Check disk space
df -h

# Check memory usage
free -m
```

---

## 🔒 Maintenance Tasks

### Daily Tasks

```bash
# Check service health
docker-compose ps

# Monitor logs for errors
docker-compose logs | grep ERROR

# Verify backups completed
ls -lh /backups/
```

### Weekly Tasks

```bash
# Update dependencies
docker-compose pull
docker-compose up -d

# Run optimization tasks
docker-compose exec web python manage.py clearcache
docker-compose exec postgres psql -U smartlaundry -d smartlaundry -c "VACUUM ANALYZE;"

# Check database size
docker-compose exec postgres psql -U smartlaundry -d smartlaundry -c "SELECT pg_size_pretty(pg_database_size('smartlaundry'));"
```

### Monthly Tasks

```bash
# Update SSL certificate
certbot renew --force-renewal

# Review and optimize database indexes
docker-compose exec web python manage.py analyzedb

# Check system security
docker-compose exec web python manage.py check --deploy

# Archive old logs
docker-compose exec web python manage.py rotate_logs
```

### Quarterly Tasks

```bash
# Full database backup to external storage
docker-compose exec postgres pg_dump -U smartlaundry smartlaundry | gzip > /backups/full_backup.sql.gz
aws s3 cp /backups/full_backup.sql.gz s3://smartlaundry-backups/

# Performance testing
# Load test the API with load testing tools

# Security audit
# Run security scanner
```

---

## 🚀 Scaling for Growth

### Scale Web Workers

```yaml
# docker-compose.yml - increase workers
web:
  command: >
    gunicorn --workers 8
    --worker-class uvicorn.workers.UvicornWorker
    backend.asgi:application
```

### Scale Celery Workers

```yaml
# docker-compose.yml - add more celery workers
celery_worker_2:
  build: .
  command: celery -A backend worker -l info --concurrency=4
  depends_on:
    - postgres
    - redis
```

### Use Load Balancer

```bash
# Install HAProxy for load balancing
apt-get install -y haproxy

# Configure multiple backend servers
# Point DNS to load balancer
# Load balancer distributes traffic across servers
```

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_order_user ON orders_order(user_id);
CREATE INDEX idx_order_status ON orders_order(status);
CREATE INDEX idx_message_room ON messaging_message(room_id);

-- Monitor slow queries
SET log_min_duration_statement = 1000;  -- Log queries > 1 second
```

---

## 🔧 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs web

# Common issues:
# - Port already in use
# - Database credentials wrong
# - Migrations not applied

# Solutions:
docker-compose down  # Stop all services
docker-compose up -d  # Start again
```

### Database Connection Error

```bash
# Test connection
docker-compose exec postgres psql -U smartlaundry -d smartlaundry

# Check credentials in .env
cat .env | grep DB_

# Restart postgres
docker-compose restart postgres
```

### Static Files Not Loading

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --clear --noinput

# Check permissions
docker-compose exec web ls -la /var/www/smartlaundry/static/

# Restart nginx
docker-compose restart nginx
```

### Celery Tasks Not Running

```bash
# Check celery worker status
docker-compose exec celery_worker celery -A backend inspect active

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart celery
docker-compose restart celery_worker
```

### High Memory Usage

```bash
# Identify memory hogs
docker stats

# Check Python memory
docker-compose exec web ps aux | grep python

# Restart service
docker-compose restart web

# Optimize in settings_production.py:
# - Reduce DATABASE connection pool
# - Reduce cache size
# - Implement pagination
```

---

## 🔄 Backup & Recovery

### Automated Backups

```bash
# Add to crontab (as root)
crontab -e

# Daily database backup at 2 AM
0 2 * * * cd /opt/smartlaundry && docker-compose exec -T postgres pg_dump -U smartlaundry smartlaundry > /backups/db_$(date +\%Y\%m\%d).sql

# Weekly media backup
0 3 * * 0 tar -czf /backups/media_$(date +\%Y\%m\%d).tar.gz /opt/smartlaundry/media/

# Upload to S3
30 3 * * * aws s3 sync /backups/ s3://smartlaundry-backups/ --delete
```

### Restore from Backup

```bash
# Restore database
docker-compose exec postgres psql -U smartlaundry smartlaundry < /backups/db_20240101.sql

# Restore media files
tar -xzf /backups/media_20240101.tar.gz -C /

# Restart services
docker-compose restart
```

---

## 📈 Performance Monitoring

### Key Metrics to Monitor

```
- API response time (target: <500ms)
- Database query time (target: <100ms)
- Cache hit rate (target: >80%)
- Error rate (target: <0.1%)
- Uptime (target: 99.9%)
- CPU usage (warning: >80%, critical: >95%)
- Memory usage (warning: >80%, critical: >95%)
- Disk usage (warning: >80%, critical: >95%)
```

### Setup Monitoring

```bash
# Option 1: Datadog
pip install datadog
# Configure environment variables

# Option 2: New Relic
pip install newrelic
# Configure APM

# Option 3: Prometheus + Grafana
docker-compose up -d prometheus grafana
```

---

## ✅ Post-Deployment Checklist

- [ ] All services running (docker-compose ps)
- [ ] API responding (curl /api/health/)
- [ ] Admin panel accessible
- [ ] WebSocket connections working
- [ ] Static files serving
- [ ] Media files accessible
- [ ] Database connected
- [ ] Redis cache working
- [ ] Celery workers active
- [ ] SSL certificate installed
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Logs flowing
- [ ] Domain pointing to server
- [ ] Health checks passing

---

**🎉 Deployment Complete!**

Your SmartLaundry platform is now live and ready for production traffic.

For ongoing support and troubleshooting, refer to logs and monitoring dashboards.
