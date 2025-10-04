# 🎉 PostgreSQL Installation Complete!

## ✅ What's Done:
1. ✓ PostgreSQL 15.14 installed successfully
2. ✓ Python packages installed (psycopg, python-dotenv)
3. ✓ Django settings updated for PostgreSQL
4. ✓ `.env` file created

## 🚀 Final Steps (Do These Now):

### Step 1: Update Password in .env File

The PostgreSQL installation created a default password. You need to update it in your `.env` file:

1. Open: `c:\xampp\htdocs\TCU_CEAA\backend\.env`
2. Replace `your_password_here` with `postgres` (or the password you set during installation)

The line should look like:
```
DB_PASSWORD=postgres
```

**Note:** If you set a custom password during installation, use that instead.

### Step 2: Add PostgreSQL to PATH (for this session)

Run this in your PowerShell:
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"
```

### Step 3: Create the Database

```powershell
# You'll be prompted for the postgres password
psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;"
```

**OR** if that doesn't work:
```powershell
# Login first
psql -U postgres

# Then in the psql prompt (postgres=#):
CREATE DATABASE tcu_ceaa_db;
\q
```

### Step 4: Run Django Migrations

```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py migrate
```

### Step 5: Create Admin User

```powershell
python manage.py createsuperuser
```

### Step 6: Start the Server

```powershell
python manage.py runserver
```

---

## 🔧 Quick Alternative: Run the Setup Script

I've created an automated script that will do Steps 1-4 for you:

```powershell
cd c:\xampp\htdocs\TCU_CEAA
.\complete_postgres_setup.ps1
```

This script will:
- Ask for your PostgreSQL password
- Update the .env file
- Create the database
- Run migrations

---

## ⚠️ Troubleshooting

### If PostgreSQL password is not working:

The default credentials are usually:
- Username: `postgres`
- Password: `postgres` OR the password you set during installation

### If you forgot the password:

You can reset it:
1. Find `pg_hba.conf` (usually in `C:\Program Files\PostgreSQL\15\data\`)
2. Change authentication method to `trust` temporarily
3. Restart PostgreSQL service
4. Reset password with: `ALTER USER postgres PASSWORD 'newpassword';`
5. Change `pg_hba.conf` back to original settings

### PostgreSQL Service Not Running:

```powershell
# Start the service
net start postgresql-x64-15
```

---

## 📝 What to Do Next:

Choose ONE of these options:

**Option A (Automated):**
```powershell
.\complete_postgres_setup.ps1
```

**Option B (Manual):**
1. Edit `backend\.env` and set DB_PASSWORD
2. Run: `psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;"`
3. Run: `cd backend; python manage.py migrate`
4. Run: `python manage.py createsuperuser`

Let me know which option you prefer!
