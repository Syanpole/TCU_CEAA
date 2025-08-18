# TCU CEAA

This is a simple web application with a Django backend and React frontend.

## What you need

- Python 3.8 or newer
- Node.js
- Basic knowledge of Django and React

## Getting started

### Backend (Django)

1. Go to the backend folder:
   ```
   cd backend
   ```

2. Install Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   python manage.py migrate
   ```

4. Start the Django server:
   ```
   python manage.py runserver
   ```

The backend will run at http://localhost:8000

### Frontend (React)

1. Go to the frontend folder:
   ```
   cd frontend
   ```

2. Install Node packages:
   ```
   npm install
   ```

3. Start the React development server:
   ```
   npm start
   ```

The frontend will run at http://localhost:3000

## Quick start (Windows)

You can also use the batch files:
- Run `start-django.bat` for the backend
- Run `start-react.bat` for the frontend

## What's included

- Django REST API backend
- React frontend with TypeScript
- User authentication
- Basic dashboard interface

## Need help?

Check the Django and React documentation if you run into issues. The project structure is pretty standard for both frameworks.
