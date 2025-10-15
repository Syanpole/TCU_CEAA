# TCU CEAA Deployment Guide

## Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 13+
- Git

## Local Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Production Deployment

### Environment Variables
Create a `.env` file in the backend directory:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:pass@localhost:5432/tcu_ceaa
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Database Setup
```bash
createdb tcu_ceaa
python manage.py migrate
python manage.py collectstatic
```

### Web Server Configuration
Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/your/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## CI/CD Pipeline Features

- **Automated Testing**: Runs Django and React tests
- **Code Quality**: Linting and style checks
- **Security Scanning**: Dependency vulnerability checks
- **Build Artifacts**: Creates deployment packages
- **Multi-environment**: Supports staging and production

## Monitoring and Logging

### Health Checks
- Backend: `GET /api/health/`
- Frontend: Available through build process

### Log Files
- Django logs: Check `backend/logs/`
- Application errors: Monitor Django admin or log aggregation service
