# Scripts Directory

This directory contains all utility and setup scripts organized by purpose.

## Structure

### setup/
Installation and dependency setup scripts:
- `install_ai_dependencies.ps1`: Install AI/ML dependencies
- `install_tesseract.ps1`: Install OCR dependencies
- `install_ci_dependencies.py`: CI/CD dependency setup

### database/
PostgreSQL and database setup scripts:
- `setup_postgresql17_database.ps1`: Main PostgreSQL setup
- `reset_postgres_password.ps1`: Password reset utilities
- `test_pgadmin_connection.ps1`: Connection testing

### Root Level
- Batch files for starting services (Django, React, PostgreSQL)
- Quick setup and fix utilities

## Usage

Run scripts from the project root directory:
```bash
# Install AI dependencies
.\scripts\setup\install_ai_dependencies.ps1

# Setup database
.\scripts\database\setup_postgresql17_database.ps1

# Start services
.\scripts\start_django.bat
.\scripts\start-react.bat
```