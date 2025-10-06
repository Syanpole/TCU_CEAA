# Step-by-Step PostgreSQL Installation and Setup

## Step 1: Install PostgreSQL

### Option A: Using Chocolatey (Recommended - Fastest)
If you have Chocolatey installed:
```powershell
choco install postgresql --version=15.8 -y
```

### Option B: Using Winget (Windows Package Manager)
```powershell
winget install --id PostgreSQL.PostgreSQL.15
```

### Option C: Manual Download (If above don't work)
1. Download PostgreSQL 15 installer from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Run the installer (postgresql-15.8-1-windows-x64.exe)
3. During installation:
   - Remember the password you set for 'postgres' user
   - Port: 5432 (default)
   - Locale: Default
4. Add to PATH if not added automatically:
   - Typical location: `C:\Program Files\PostgreSQL\15\bin`

---

## Step 2: Verify PostgreSQL Installation

Open a NEW PowerShell window (to refresh PATH) and run:
```powershell
psql --version
```

You should see something like: `psql (PostgreSQL) 15.x`

---

## Step 3: Create Environment File

1. Navigate to backend folder:
```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
```

2. Create `.env` file from template:
```powershell
Copy-Item .env.example .env
```

3. Edit `.env` file and update with your PostgreSQL password:
```env
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD_HERE
DB_HOST=localhost
DB_PORT=5432
```

**IMPORTANT:** Replace `YOUR_POSTGRES_PASSWORD_HERE` with the password you set during PostgreSQL installation!

---

## Step 4: Create Database

```powershell
# You'll be prompted for the postgres password
psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;"
```

Alternative method if above doesn't work:
```powershell
# Login to PostgreSQL
psql -U postgres

# Then in the psql prompt, run:
CREATE DATABASE tcu_ceaa_db;
\q
```

---

## Step 5: Run Django Migrations

```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py makemigrations
python manage.py migrate
```

---

## Step 6: Create Superuser

```powershell
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## Step 7: Migrate Existing Data (Optional)

If you have existing data in SQLite that you want to keep:

```powershell
# 1. First, temporarily switch back to SQLite in settings.py
# 2. Dump the data
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > datadump.json

# 3. Switch back to PostgreSQL in settings.py
# 4. Run migrations (if not done already)
python manage.py migrate

# 5. Load the data
python manage.py loaddata datadump.json
```

---

## Step 8: Start the Server

```powershell
python manage.py runserver
```

Visit http://localhost:8000/admin to verify everything works!

---

## Troubleshooting

### "psql: command not found" or "not recognized"
- PostgreSQL is not installed or not in PATH
- Restart PowerShell after installation
- Manually add to PATH: `C:\Program Files\PostgreSQL\15\bin`

### "Connection to server failed"
- PostgreSQL service not running
- Start it: `net start postgresql-x64-15` (name may vary)
- Or use Windows Services (services.msc)

### "password authentication failed"
- Wrong password in `.env` file
- Use the password you set during PostgreSQL installation

### "database does not exist"
- Run the CREATE DATABASE command from Step 4

### Port 5432 already in use
- Another service is using that port
- Change port in PostgreSQL config or in your `.env` file

---

## Quick Commands Reference

```powershell
# Check PostgreSQL status
Get-Service -Name postgresql*

# Start PostgreSQL service
net start postgresql-x64-15

# Stop PostgreSQL service  
net stop postgresql-x64-15

# Connect to database
psql -U postgres -d tcu_ceaa_db

# List databases
psql -U postgres -c "\l"

# Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
