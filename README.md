# TCU CEAA - Django React Application

A full-stack web application built with Django REST Framework backend and React TypeScript frontend, styled with TailwindCSS.

## Project Structure

```
TCU_CEAA/
├── django-react-app/
│   ├── backend/                 # Django REST API
│   │   ├── backend_project/     # Django project settings
│   │   ├── myapp/              # Main Django app
│   │   ├── manage.py           # Django management script
│   │   ├── requirements.txt    # Python dependencies
│   │   └── .env               # Environment variables
│   └── frontend/               # React TypeScript app
│       ├── src/               # React source code
│       ├── public/            # Static files
│       ├── package.json       # Node.js dependencies
│       └── tailwind.config.js # TailwindCSS configuration
├── setup.py                   # Setup script
├── start-django.bat           # Django server launcher
└── start-react.bat            # React server launcher
```

## Features

- **Backend (Django)**:
  - REST API with Django REST Framework
  - PostgreSQL database integration
  - CORS enabled for frontend communication
  - Task and Student models with full CRUD operations

- **Frontend (React)**:
  - TypeScript for type safety
  - Axios for API communication
  - TailwindCSS for styling
  - Responsive design

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Git

## Quick Setup

### Option 1: Automated Setup
```bash
# Setup everything
python setup.py all

# Or setup individually
python setup.py django
python setup.py react
```

### Option 2: Manual Setup

#### Backend Setup
1. Navigate to backend directory:
   ```bash
   cd django-react-app/backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure database in `.env` file:
   ```
   DB_NAME=tcu_ceaa_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

#### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd django-react-app/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Method 1: Using Batch Files (Windows)
- Double-click `start-django.bat` to start the backend server
- Double-click `start-react.bat` to start the frontend server

### Method 2: Manual Start
1. Start Django backend:
   ```bash
   cd django-react-app/backend
   python manage.py runserver
   ```

2. Start React frontend (in new terminal):
   ```bash
   cd django-react-app/frontend
   npm start
   ```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoints**:
  - Tasks: http://localhost:8000/api/tasks/
  - Students: http://localhost:8000/api/students/

## API Endpoints

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get specific task
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Students
- `GET /api/students/` - List all students
- `POST /api/students/` - Create new student
- `GET /api/students/{id}/` - Get specific student
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student

## Development

### Adding New Features
1. Backend: Add models in `myapp/models.py`, create serializers, and views
2. Frontend: Create components in `src/components/`
3. Styling: Use TailwindCSS classes for consistent styling

### Database Changes
```bash
python manage.py makemigrations
python manage.py migrate
```

### Frontend Dependencies
```bash
npm install package-name
```

### Backend Dependencies
```bash
pip install package-name
pip freeze > requirements.txt
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure `corsheaders` is installed and configured in Django settings
2. **Database Connection**: Check PostgreSQL is running and credentials are correct
3. **TailwindCSS not working**: Ensure the build process includes PostCSS processing
4. **API 404 Errors**: Verify Django URLs are correctly configured

### Database Reset
```bash
python manage.py flush
python manage.py migrate
```

## Technologies Used

- **Backend**: Django 5.2.5, Django REST Framework 3.14.0, PostgreSQL
- **Frontend**: React 19.1.1, TypeScript 4.9.5, Axios 1.11.0
- **Styling**: TailwindCSS 3.4.0
- **Development**: Node.js, Python, Git

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
