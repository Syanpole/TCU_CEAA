# PostgreSQL Database Setup Guide

## Prerequisites
1. Install PostgreSQL from https://www.postgresql.org/download/windows/
   - Or via Chocolatey: `choco install postgresql`
   - Default username is usually `postgres`
   - Remember the password you set during installation

## Automatic Setup (Recommended)

Run the setup script:
```powershell
.\setup_postgresql.ps1
```

This will:
- Check if PostgreSQL is installed
- Create a database for the project
- Set up environment variables
- Install required Python packages
- Run Django migrations

## Manual Setup

### 1. Create PostgreSQL Database

Open PowerShell or Command Prompt and run:

```powershell
# Login to PostgreSQL (you'll be prompted for password)
psql -U postgres

# Once logged in, create the database:
CREATE DATABASE tcu_ceaa_db;

# Create a user (optional, or use postgres user):
CREATE USER tcu_user WITH PASSWORD 'your_secure_password';

# Grant privileges:
GRANT ALL PRIVILEGES ON DATABASE tcu_ceaa_db TO tcu_user;

# Exit psql:
\q
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend` folder:

```env
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=django-insecure-02x_h8khitxe9-e(trptwbdz&wirq@&lsu6odgbu15stm_#*0x
DEBUG=True
```

**Important:** Replace `your_password_here` with your actual PostgreSQL password!

### 3. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 4. Run Django Migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```powershell
python manage.py createsuperuser
```

### 6. Start the Server

```powershell
python manage.py runserver
```

## Troubleshooting

### Connection Refused Error
- Make sure PostgreSQL service is running
- Windows: Check Services (services.msc) for "postgresql" service
- Or run: `net start postgresql-x64-15` (version may vary)

### Authentication Failed
- Double-check your password in the `.env` file
- Make sure the user has proper permissions

### Database Does Not Exist
- Create the database manually using the SQL commands above
- Or run the setup script

### Port Already in Use
- Default PostgreSQL port is 5432
- Check if another service is using it or change the port in `.env`

## Switching Back to SQLite

If you need to switch back to SQLite, edit `backend/backend_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Database Migration from SQLite

If you have existing data in SQLite:

```powershell
# 1. Dump data from SQLite
python manage.py dumpdata > datadump.json

# 2. Switch to PostgreSQL (edit settings.py)

# 3. Run migrations
python manage.py migrate

# 4. Load data into PostgreSQL
python manage.py loaddata datadump.json
```

## Verifying the Connection

Test the database connection:

```powershell
python manage.py dbshell
```

This should open a PostgreSQL prompt if the connection is successful.
