# 🧪 TCU-CEAA Testing Guide

## Quick Start

### Run All Tests
```powershell
.\run_all_tests.ps1
```

### Run Backend Tests Only
```powershell
.\test_backend.ps1
```

### Run Frontend Tests Only
```powershell
.\test_frontend.ps1
```

### Run Frontend Tests with Coverage
```powershell
.\test_frontend_coverage.ps1
```

---

## 📋 Test Files Available

### Backend Test Files
Located in `backend/`:
- ✅ `myapp/tests.py` - Core authentication & user model tests (ACTIVE)
- `test_ai_algorithms.py` - AI algorithm demonstrations
- `test_ai_integration.py` - AI integration tests
- `test_ai_performance.py` - AI performance tests
- `test_ai_verification.py` - AI verification tests
- `test_admin_dashboard_api.py` - Admin dashboard API tests
- `test_authentication.py` - Authentication flow tests
- `test_api_login.py` - API login endpoint tests
- `test_decision_logic.py` - Decision logic tests
- `test_ci_dependency_resolution.py` - CI/CD dependency tests

### Frontend Test Files
Located in `frontend/src/`:
- ✅ `App.test.tsx` - App component tests (ACTIVE)
- ✅ `utils/numberUtils.test.ts` - Number utility tests (ACTIVE)

---

## 🔧 Manual Test Commands

### Backend (Django)

```powershell
# Navigate to backend
cd backend

# Run all tests
python manage.py test

# Run specific test module
python manage.py test myapp.tests

# Run specific test case
python manage.py test myapp.tests.AuthenticationTestCase

# Run specific test method
python manage.py test myapp.tests.AuthenticationTestCase.test_user_login

# Run with verbosity
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb

# Run with coverage (requires pytest-cov)
pytest --cov=myapp --cov-report=html
```

### Frontend (React)

```powershell
# Navigate to frontend
cd frontend

# Run tests in watch mode
npm test

# Run all tests once
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test -- App.test.tsx --watchAll=false

# Update snapshots
npm test -- -u --watchAll=false

# Run in CI mode
npm run test:ci
```

---

## 📊 Test Coverage

### Current Coverage

#### Backend
- **Authentication:** ✅ 100%
- **User Models:** ✅ 100%
- **API Endpoints:** ⚠️ Partial
- **AI Algorithms:** ⚠️ Pending
- **Database Models:** ✅ Via migrations

#### Frontend
- **Core Components:** ⚠️ Partial
- **Utility Functions:** ✅ 100%
- **App Component:** ✅ Basic

---

## 🎯 Writing New Tests

### Backend Test Template

Create a new test file in `backend/myapp/tests/`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class MyFeatureTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_my_feature(self):
        """Test my specific feature"""
        # Arrange
        # Act
        # Assert
        self.assertEqual(1 + 1, 2)
    
    def tearDown(self):
        """Clean up after tests"""
        self.user.delete()
```

### Frontend Test Template

Create a new test file in `frontend/src/components/`:

```typescript
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders without crashing', () => {
    render(<MyComponent />);
  });

  it('displays correct text', () => {
    render(<MyComponent />);
    const element = screen.getByText(/expected text/i);
    expect(element).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    const { getByRole } = render(<MyComponent />);
    const button = getByRole('button');
    
    // fireEvent.click(button);
    // expect(/* something changed */).toBe(true);
  });
});
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Issue: Tests fail with database errors
**Solution:**
```powershell
# Recreate test database
python manage.py test --keepdb=false

# Or migrate the test database
python manage.py migrate --run-syncdb
```

#### Issue: Unicode/Emoji errors in Windows
**Solution:**
```powershell
# Set UTF-8 encoding
$env:PYTHONIOENCODING = 'utf-8'
python manage.py test
```

#### Issue: Import errors
**Solution:**
```powershell
# Install missing dependencies
pip install -r requirements.txt

# Or install specific package
pip install <package-name>
```

### Frontend Issues

#### Issue: Tests hang or don't exit
**Solution:**
```powershell
# Run with --watchAll=false
npm test -- --watchAll=false
```

#### Issue: Module not found errors
**Solution:**
```powershell
# Reinstall node modules
rm -r node_modules package-lock.json
npm install
```

#### Issue: Coverage not generating
**Solution:**
```powershell
# Clean and regenerate
rm -r coverage
npm test -- --coverage --watchAll=false
```

---

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          python manage.py test myapp.tests

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --watchAll=false --coverage
```

---

## 🎓 Best Practices

### 1. Test Organization
- Keep tests close to the code they test
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Test Coverage
- Aim for 80%+ coverage on critical paths
- 100% coverage on utility functions
- Don't test framework code

### 3. Test Speed
- Keep unit tests fast (< 1s each)
- Use mocks for external dependencies
- Run integration tests separately

### 4. Test Maintenance
- Update tests when code changes
- Remove obsolete tests
- Keep test data realistic

### 5. Continuous Testing
- Run tests before committing
- Use pre-commit hooks
- Integrate with CI/CD

---

## 📚 Resources

### Backend Testing
- [Django Testing Documentation](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)

### Frontend Testing
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

## ✅ Current Test Status

**Last Updated:** October 5, 2025

| Component | Status | Tests | Passing |
|-----------|--------|-------|---------|
| Backend Core | ✅ | 4 | 4 |
| Frontend Core | ✅ | 8 | 8 |
| **Total** | **✅** | **12** | **12** |

**Overall Status:** ✅ **ALL TESTS PASSING**

---

## 🚀 Next Steps

1. ✅ Basic unit tests implemented
2. ⏳ Add more component tests (Frontend)
3. ⏳ Add API endpoint tests (Backend)
4. ⏳ Add integration tests
5. ⏳ Set up E2E testing (Cypress/Playwright)
6. ⏳ Implement test coverage requirements
7. ⏳ Add CI/CD pipeline integration

---

**Happy Testing! 🧪**
