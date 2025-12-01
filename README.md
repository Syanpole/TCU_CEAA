# TCU CEAA - College Educational Assistance Application

## 📋 Overview
Taguig City University College Educational Assistance Application (TCU CEAA) is a comprehensive web application that automates the processing and verification of educational assistance applications using AI-powered document verification.

## 🚀 Live Deployment
- **Frontend**: https://tcu-ceaa-8863d.web.app
- **Backend**: https://tcu-ceaa-backend-1039894841462.us-central1.run.app
- **Platform**: GCP Cloud Run + Firebase Hosting + AWS AI Services

## 🏗️ Tech Stack

### Frontend
- React 18 with TypeScript
- Firebase Hosting
- Material-UI components
- Axios for API calls

### Backend
- Django 5.2.5 + Django REST Framework
- PostgreSQL 14 (Cloud SQL)
- Python 3.11 with AI/ML libraries

### Infrastructure
- **GCP**: Cloud Run (serverless), Cloud SQL, Artifact Registry
- **AWS**: S3 (document storage), Textract (OCR), Rekognition (face verification)
- **Database**: PostgreSQL with pgvector extension

### AI/ML Capabilities
- **YOLO v8** - Document detection (COE, ID, voter certificates)
- **PyTorch** - Deep learning models
- **AWS Textract** - Grade OCR extraction
- **AWS Rekognition** - Face liveness detection and matching
- **6 AI Algorithms**: Document validator, cross-document matcher, grade verifier, face verifier, fraud detector, AI verification manager

## 📁 Project Structure
```
TCU_CEAA/
├── backend/               # Django backend
│   ├── backend_project/   # Main project settings
│   ├── myapp/            # Main application
│   ├── ai_models/        # YOLO models
│   └── Dockerfile.prod   # Production Docker image
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   └── contexts/     # React contexts
│   ├── firebase.json     # Firebase hosting config
│   └── Dockerfile.prod   # Production Docker image
└── docs/                 # Documentation
```

## 🔧 Setup & Deployment

### Prerequisites
- GCP Project with billing enabled
- AWS account with S3, Textract, Rekognition access
- Firebase project
- Docker installed locally
- gcloud CLI
- Node.js 18+
- Python 3.11+

### Environment Variables

**Backend** (Cloud Run):
```bash
DEBUG=False
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=<your-db-password>
DB_HOST=/cloudsql/<project>:<region>:<instance>
SECRET_KEY=<django-secret-key>
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET_NAME=tcu-ceaa-documents
AWS_COGNITO_IDENTITY_POOL_ID=<cognito-pool-id>
```

**Frontend** (Build time):
```bash
REACT_APP_API_URL=https://tcu-ceaa-backend-1039894841462.us-central1.run.app
```

### Quick Deploy

**Backend:**
```bash
cd backend
docker build -f Dockerfile.prod -t us-central1-docker.pkg.dev/<project>/tcu-ceaa-repo/backend:latest .
docker push us-central1-docker.pkg.dev/<project>/tcu-ceaa-repo/backend:latest

gcloud run deploy tcu-ceaa-backend \
  --image=us-central1-docker.pkg.dev/<project>/tcu-ceaa-repo/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=8080 \
  --memory=4Gi \
  --cpu=2 \
  --timeout=300 \
  --set-cloudsql-instances=<connection-name> \
  --set-env-vars="<env-vars>"
```

**Frontend:**
```bash
cd frontend
REACT_APP_API_URL="<backend-url>" npm run build
firebase deploy --only hosting
```

## 👤 Admin Credentials
- **Username**: admin
- **Email**: admin@tcu.edu.ph
- **Password**: TCUAdmin2024!

## 📚 Key Documentation
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `GCP_AWS_HYBRID_DEPLOYMENT_GUIDE.md` - Hybrid cloud setup
- `FACE_VERIFICATION_GUIDE.md` - Face verification implementation
- `ADMIN_QUICK_START_GUIDE.md` - Admin user guide
- `SECURITY_HARDENING_COMPLETE.md` - Security measures
- `AUTO_APPROVAL_SYSTEM_COMPLETE.md` - AI auto-approval system
- `S3_ENFORCEMENT_COMPLETE.md` - S3 storage enforcement

## 🔐 Security Features
- JWT authentication
- CORS protection
- Django security middleware
- AWS S3 presigned URLs
- Face liveness detection
- Document tampering detection
- SQL injection prevention
- XSS protection

## 📊 Key Features
1. **Student Registration** - Email verification, document upload
2. **Document Verification** - AI-powered COE, ID, birth certificate, voter certificate verification
3. **Grade Submission** - Per-subject grade upload with OCR extraction
4. **Face Verification** - AWS Rekognition liveness detection
5. **Admin Dashboard** - Application review, adjudication, analytics
6. **AI System** - 6 AI algorithms with confidence scoring
7. **Auto-Approval** - Automated approval for high-confidence applications

## 🛠️ Development

### Local Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Local Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📝 API Endpoints
All endpoints are prefixed with `/api/`:
- `/api/auth/` - Authentication (login, register, logout)
- `/api/documents/` - Document submissions
- `/api/grades/` - Grade submissions
- `/api/applications/` - Allowance applications
- `/api/ai/` - AI verification endpoints
- `/api/face-verification/` - Face verification endpoints
- `/api/admin/` - Admin management

## 💰 Cost Estimation (2 weeks)
- **GCP Cloud Run**: ~$84 (4Gi RAM, 2 vCPU)
- **GCP Cloud SQL**: ~$50 (db-custom-1-3840)
- **AWS S3**: ~$5 (storage + requests)
- **AWS Textract**: ~$10 (OCR processing)
- **AWS Rekognition**: ~$20 (face liveness)
- **Total**: ~$150-170 for 2 weeks

## 🐛 Known Issues & Solutions
- **Cold Start**: First request after idle takes 7-8 seconds (YOLO models loading)
- **Memory**: Backend requires 4Gi RAM for PyTorch + YOLO
- **CORS**: Ensure Firebase URLs in CORS_ALLOWED_ORIGINS

## 🤝 Contributing
This is a thesis project for Taguig City University. For questions or issues, contact the development team.

## 📄 License
Educational use only - Taguig City University

## 🎓 Thesis Information
- **Institution**: Taguig City University
- **Purpose**: Thesis presentation and demonstration
- **Duration**: 2 weeks active deployment
- **Year**: 2025
