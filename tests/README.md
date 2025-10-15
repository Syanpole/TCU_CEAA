# Tests Directory

This directory contains all test files organized by category:

## Structure

### backend/
- **ai_tests/**: All AI-related test files (document verification, AI detection, algorithms)
- **django_tests/**: Django framework tests (database, authentication, models)
- **integration_tests/**: Integration and system-wide tests

### frontend/
- Frontend component and service tests (moved from frontend/src)

## Running Tests

### Backend Tests
```bash
cd backend
python -m pytest tests/backend/ai_tests/
python -m pytest tests/backend/django_tests/
python -m pytest tests/backend/integration_tests/
```

### All Tests
```bash
python -m pytest tests/
```