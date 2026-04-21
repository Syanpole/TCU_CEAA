# Docker Deployment Guide for TCU CEAA

This guide covers Docker-based deployment options for the TCU CEAA application.

## Architecture Options

### Option 1: Full Docker Compose (Recommended for Development/Testing)
All services run in Docker containers with Nginx as reverse proxy.

```
┌─────────────────────────────────────────┐
│           Nginx (Port 80/443)           │
│  ┌────────────────────────────────────┐ │
│  │   React Static Files (/)           │ │
│  │   API Proxy (/api/) → Backend      │ │
│  └────────────────────────────────────┘ │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼─────┐
│  Django    │    │ PostgreSQL │
│  Backend   │    │  Database  │
│  (Port     │    │  (Port     │
│   8000)    │    │   5432)    │
└────────────┘    └────────────┘
```

### Option 2: Hybrid (GCP Cloud Run + Firebase)
Backend on Cloud Run, Frontend on Firebase Hosting.

```
┌─────────────────────┐      ┌──────────────────┐
│ Firebase Hosting    │      │  GCP Cloud Run   │
│ (React Frontend)    │─────▶│  (Django Backend)│
│ https://...web.app  │ API  │  Port 8080       │
└─────────────────────┘      └────────┬─────────┘
                                      │
                              ┌───────▼────────┐
                              │  Cloud SQL     │
                              │  (PostgreSQL)  │
                              └────────────────┘
```

## Quick Start

### Option 1: Full Docker Compose Setup

1. **Create environment file:**
```bash
cp backend/.env.example .env
# Edit .env with your configuration
```

2. **Build and start all services:**
```bash
docker-compose up -d --build
```

3. **Run migrations:**
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

4. **Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost/api/
- Admin Panel: http://localhost/admin/

5. **View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f nginx
```

6. **Stop services:**
```bash
docker-compose down
```

### Option 2: Separate Frontend Container

1. **Build frontend Docker image:**
```bash
cd frontend
docker build -t tcu-ceaa-frontend:latest .
```

2. **Run frontend container:**
```bash
docker run -d -p 3000:80 --name tcu-ceaa-frontend tcu-ceaa-frontend:latest
```

3. **Access frontend:**
http://localhost:3000

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DB_NAME=tcu_ceaa
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# GCP (if using Cloud SQL)
GCP_PROJECT_ID=your-project-id
CLOUD_SQL_CONNECTION_NAME=your-connection-name

# Firebase
FIREBASE_API_KEY=your-api-key
FIREBASE_PROJECT_ID=your-project-id
```

## Production Deployment

### SSL/HTTPS Setup

1. **Obtain SSL certificates** (Let's Encrypt recommended):
```bash
certbot certonly --standalone -d yourdomain.com
```

2. **Update nginx.conf** to enable HTTPS:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of configuration
}
```

3. **Mount certificates in docker-compose.yml:**
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### GCP Cloud Run Deployment

1. **Build and push backend image:**
```bash
cd backend
docker build -t us-central1-docker.pkg.dev/YOUR-PROJECT/cloud-run-source-deploy/tcu-ceaa-backend:latest .
docker push us-central1-docker.pkg.dev/YOUR-PROJECT/cloud-run-source-deploy/tcu-ceaa-backend:latest
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy tcu-ceaa-backend \
  --image us-central1-docker.pkg.dev/YOUR-PROJECT/cloud-run-source-deploy/tcu-ceaa-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-cloudsql-instances "YOUR-PROJECT:us-central1:tcu-ceaa-postgres" \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### Firebase Hosting Deployment

1. **Build React app:**
```bash
cd frontend
npm run build
```

2. **Deploy to Firebase:**
```bash
firebase deploy --only hosting
```

3. **Update .env to point to Cloud Run backend:**
```env
REACT_APP_API_URL=https://your-cloud-run-url.run.app/api
```

## Monitoring and Logs

### Docker Compose
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 backend
```

### GCP Cloud Run
```bash
# View logs
gcloud run services logs read tcu-ceaa-backend --region us-central1

# Stream logs
gcloud run services logs tail tcu-ceaa-backend --region us-central1
```

## Troubleshooting

### Issue: Backend container can't connect to database
```bash
# Check database container status
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify connection from backend
docker-compose exec backend python manage.py dbshell
```

### Issue: Nginx 502 Bad Gateway
```bash
# Check backend is running
docker-compose ps backend

# Check backend health
curl http://localhost:8000/health

# Check nginx configuration
docker-compose exec nginx nginx -t
```

### Issue: Frontend can't reach API
1. Check browser console for CORS errors
2. Verify API_URL in frontend .env
3. Check nginx proxy configuration
4. Verify backend ALLOWED_HOSTS setting

## Performance Optimization

### Nginx Caching
Add to nginx.conf:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 302 10m;
    proxy_cache_valid 404 1m;
}
```

### Database Connection Pooling
Update backend settings.py:
```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

## Backup and Restore

### Database Backup
```bash
docker-compose exec db pg_dump -U postgres tcu_ceaa > backup.sql
```

### Database Restore
```bash
cat backup.sql | docker-compose exec -T db psql -U postgres tcu_ceaa
```

## Security Checklist

- [ ] Change default passwords
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set strong SECRET_KEY
- [ ] Enable Django security middleware
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Enable database encryption
- [ ] Configure backup strategy

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Verify environment variables
- Review nginx configuration
- Check Django settings
- Consult deployment documentation
