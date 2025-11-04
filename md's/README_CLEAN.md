# TCU CEAA - Clean & Organized

A comprehensive document verification system with AI-powered fraud detection for TCU CEAA.

## 📁 **Project Structure (Cleaned & Organized)**

```
TCU_CEAA/
├── 📄 README.md                 # This file
├── 🐳 docker-compose.yml        # Container orchestration
├── 🔧 setup.py                  # Python setup configuration
├── 📜 QUICK_START.txt           # Quick start guide
│
├── 🖥️  backend/                  # Django API server
│   ├── manage.py
│   ├── requirements.txt
│   ├── ai_verification/         # AI algorithms
│   ├── myapp/                   # Main Django app
│   └── backend_project/         # Django settings
│
├── 🌐 frontend/                  # React TypeScript UI
│   ├── package.json
│   ├── src/                     # React components
│   └── public/                  # Static assets
│
├── 🧪 tests/                     # All test files (organized)
│   ├── backend/
│   │   ├── ai_tests/           # AI algorithm tests
│   │   ├── django_tests/       # Django framework tests
│   │   └── integration_tests/   # System integration tests
│   └── frontend/               # React component tests
│
├── 📚 docs/                      # Documentation
│   ├── README.md               # Main project docs
│   ├── DEPLOYMENT.md           # Deploy instructions
│   ├── guides/                 # Setup guides
│   └── AI_INTEGRATION_README.md
│
└── 🔨 scripts/                   # Utility scripts
    ├── setup/                  # Installation scripts
    ├── database/              # PostgreSQL scripts
    └── *.bat                  # Service start scripts
```

## 🚀 **Quick Start**

### 1. Backend (Django + AI)
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 2. Frontend (React)
```bash
cd frontend  
npm install
npm start
```

### 3. Run Tests
```bash
# All tests
python -m pytest tests/

# Specific test categories
python -m pytest tests/backend/ai_tests/
python -m pytest tests/backend/django_tests/
```

## ✨ **Key Features**

- 🤖 **AI Document Verification**: 6 core algorithms
- 🛡️ **Fraud Detection**: Advanced AI-powered prevention
- 📊 **Admin Dashboard**: Real-time monitoring
- 🎓 **Grade Management**: Flexible grading system
- 🔐 **Secure Authentication**: JWT + session management

## 🎯 **Cleaned Up**

✅ **Removed 50+ redundant markdown files**  
✅ **Organized all test files into `/tests` directory**  
✅ **Moved utility scripts to `/scripts` directory**  
✅ **Consolidated documentation in `/docs` directory**  
✅ **Clean project root with only essential files**

## 📖 **Documentation**

- **Setup Guides**: `docs/guides/`
- **API Documentation**: `docs/`
- **Test Documentation**: `tests/README.md`
- **Script Usage**: `scripts/README.md`

## 🏗️ **Architecture**

- **Backend**: Django 5.2.5 + PostgreSQL + AI algorithms
- **Frontend**: React 18.3 + TypeScript + Material UI components  
- **AI System**: 6 core verification algorithms with 9 detection methods
- **Database**: PostgreSQL 17 with optimized schema

---

*Clean, organized, and production-ready! 🎉*