# TCU-CEAA (Taguig City University - City Educational Assistance Allowance)

## 📋 Project Overview

The **TCU-CEAA** is a comprehensive digital platform designed to streamline the City Educational Assistance Allowance program for Taguig City University students. This web application automates the entire process from student registration and document submission to grade evaluation and allowance disbursement.

### 🎯 System Purpose

The system manages two types of educational assistance:
- **Basic Educational Assistance**: ₱5,000 for students maintaining GWA ≥ 80%
- **Merit Incentive**: ₱5,000 for exceptional students with SWA ≥ 88.75%
- **Combined Allowance**: ₱10,000 for students qualifying for both programs

### 🏗️ Architecture

This is a **full-stack web application** built with:
- **Backend**: Django 5.2.5 with Django REST Framework
- **Frontend**: React 19.1.1 with TypeScript
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT-based user authentication
- **File Storage**: Local file system with image processing

## ✨ Key Features

### 👨‍🎓 Student Features
- **Secure Registration & Login**: Create accounts with student ID validation
- **Document Management**: Upload and track required documents (birth certificate, school ID, grades, etc.)
- **Grade Submission**: Submit academic records with automatic eligibility calculation
- **Application Tracking**: Monitor allowance application status in real-time
- **Profile Management**: Update personal information and profile pictures
- **Dashboard**: Comprehensive overview of submissions and application status

### 👨‍💼 Admin Features
- **Student Management**: View and manage all registered students
- **Document Review**: Review, approve, or reject submitted documents
- **Grade Evaluation**: AI-assisted grade analysis and allowance calculation
- **Application Processing**: Process allowance applications and disbursements
- **Analytics Dashboard**: Track system usage and allowance statistics
- **Bulk Operations**: Efficient management of multiple applications

### 🤖 AI-Powered Features
- **Automatic Eligibility Assessment**: Smart evaluation of grade requirements
- **Document Validation**: Automated checks for required document types
- **Risk Assessment**: Identify applications requiring manual review
- **Performance Analytics**: Generate insights on student performance trends

## 🛠️ Technology Stack

### Backend Dependencies
```
Django==5.2.5                 # Web framework
djangorestframework==3.14.0   # REST API framework
django-cors-headers==4.3.1    # CORS handling
psycopg2-binary==2.9.7       # PostgreSQL adapter
Pillow                        # Image processing
```

### Frontend Dependencies
```
React 19.1.1                 # UI framework
TypeScript 4.9.5             # Type safety
Axios 1.11.0                 # HTTP client
React Image Crop 11.0.10     # Image cropping
```

## 📋 System Requirements

### Prerequisites
- **Python**: 3.8 or newer
- **Node.js**: 16.x or newer
- **npm**: 8.x or newer
- **Git**: Latest version
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for development
- **Processor**: Intel i3 or equivalent

## 🚀 Installation & Setup

### Option 1: Quick Start (Windows Users)

For Windows users, we provide convenient batch files:

```bash
# Start the Django backend
start-django.bat

# In a new terminal, start the React frontend
start-react.bat
```

### Option 2: Manual Setup

#### Backend Setup (Django)

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create and apply database migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Admin User** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

6. **Load Sample Data** (Optional)
   ```bash
   python create_sample_data.py
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```
   
   ✅ Backend will be available at: **http://localhost:8000**

#### Frontend Setup (React)

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```
   
   ✅ Frontend will be available at: **http://localhost:3002**

## 📁 Project Structure

```
TCU_CEAA/
├── backend/                          # Django backend application
│   ├── manage.py                     # Django management script
│   ├── requirements.txt              # Python dependencies
│   ├── db.sqlite3                    # SQLite database (development)
│   ├── backend_project/              # Django project settings
│   │   ├── settings.py               # Configuration settings
│   │   ├── urls.py                   # URL routing
│   │   └── wsgi.py                   # WSGI configuration
│   ├── myapp/                        # Main application
│   │   ├── models.py                 # Database models
│   │   ├── views.py                  # API endpoints
│   │   ├── serializers.py            # Data serialization
│   │   ├── urls.py                   # App URL patterns
│   │   └── email_utils.py            # Email functionality
│   ├── media/                        # User uploaded files
│   │   └── profile_images/           # Profile pictures
│   └── migrations/                   # Database migrations
├── frontend/                         # React frontend application
│   ├── package.json                  # Node.js dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── public/                       # Static assets
│   │   └── images/                   # Application images
│   ├── src/                          # Source code
│   │   ├── App.tsx                   # Main application component
│   │   ├── components/               # React components
│   │   │   ├── AdminDashboard.tsx    # Admin interface
│   │   │   ├── StudentDashboard.tsx  # Student interface
│   │   │   ├── Login.tsx             # Authentication
│   │   │   └── ...                   # Other components
│   │   ├── contexts/                 # React contexts
│   │   └── services/                 # API services
│   └── build/                        # Production build files
├── start-django.bat                  # Windows Django launcher
├── start-react.bat                   # Windows React launcher
└── README.md                         # This file
```

## 🔐 User Roles & Permissions

### Student Role
- Register and manage personal profile
- Submit required documents
- Upload academic grades
- Apply for educational assistance
- Track application status
- Receive notifications

### Admin Role
- Manage student accounts
- Review and approve documents
- Evaluate grade submissions
- Process allowance applications
- Generate reports and analytics
- System configuration

## 🎯 Core Workflows

### Student Application Process
1. **Registration**: Create account with valid student ID
2. **Document Submission**: Upload required documents
3. **Grade Submission**: Submit academic records
4. **AI Evaluation**: System automatically calculates eligibility
5. **Application Review**: Admin reviews and approves
6. **Disbursement**: Allowance is processed and recorded

### Admin Management Process
1. **Document Review**: Verify submitted documents
2. **Grade Validation**: Confirm academic records
3. **Eligibility Assessment**: Review AI recommendations
4. **Application Processing**: Approve or reject applications
5. **Disbursement Tracking**: Monitor payment status

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3002
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration
For production, update `settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tcu_ceaa',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
Test authentication and endpoints:
```bash
python test_auth.py
python test_login_api.py
```

## 📊 API Endpoints

### Authentication
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `POST /api/register/` - User registration

### Student Management
- `GET /api/students/` - List all students (admin only)
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update user profile

### Documents
- `POST /api/documents/` - Submit document
- `GET /api/documents/` - List user documents
- `PUT /api/documents/{id}/` - Update document status (admin)

### Grades
- `POST /api/grades/` - Submit grades
- `GET /api/grades/` - List grade submissions
- `PUT /api/grades/{id}/` - Review grades (admin)

### Applications
- `POST /api/applications/` - Apply for allowance
- `GET /api/applications/` - List applications
- `PUT /api/applications/{id}/` - Process application (admin)

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python virtual environment is activated
- Check that all requirements are installed: `pip install -r requirements.txt`
- Verify database migrations: `python manage.py migrate`

**Frontend won't start:**
- Clear node modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 16+)
- Verify package.json scripts section

**CORS Errors:**
- Ensure backend CORS settings include frontend URL
- Check that both servers are running on correct ports

**Database Errors:**
- Run migrations: `python manage.py migrate`
- Reset database: Delete `db.sqlite3` and re-run migrations

### Debug Mode
Enable debug logging in Django settings:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: Ensure all tests pass
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

### Coding Standards
- **Python**: Follow PEP 8 guidelines
- **TypeScript**: Use ESLint and Prettier
- **Commit Messages**: Use conventional commit format
- **Documentation**: Update README for new features

## 📄 License

This project is developed for Taguig City University. All rights reserved.

## 🆘 Support

For technical support or questions:

- **Email**: support@tcu-ceaa.edu.ph
- **Documentation**: Check this README and inline code comments
- **Issues**: Create GitHub issues for bugs or feature requests

### Additional Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintained by**: TCU Development Team
