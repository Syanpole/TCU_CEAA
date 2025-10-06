# Fix Login Issues & Connect to pgAdmin 4

## Problem 1: Login Failed - PostgreSQL Password Unknown

Your `.env` file still has `DB_PASSWORD=your_password_here` which is not the correct password.

### Solution A: Reset PostgreSQL Password (Easiest)

1. **Stop using password authentication temporarily:**

   Open PowerShell as Administrator:
   ```powershell
   # Navigate to PostgreSQL config directory
   cd "C:\Program Files\PostgreSQL\17\data"
   
   # Backup the current configuration
   Copy-Item pg_hba.conf pg_hba.conf.backup
   
   # Open pg_hba.conf in notepad
   notepad pg_hba.conf
   ```

2. **Edit `pg_hba.conf`:**
   
   Find these lines near the bottom:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   # IPv6 local connections:
   host    all             all             ::1/128                 scram-sha-256
   ```
   
   Change `scram-sha-256` to `trust`:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            trust
   # IPv6 local connections:
   host    all             all             ::1/128                 trust
   ```
   
   Save and close.

3. **Restart PostgreSQL service:**
   ```powershell
   Restart-Service postgresql-x64-17
   ```

4. **Set a new password:**
   ```powershell
   # Add PostgreSQL to PATH
   $env:Path = "C:\Program Files\PostgreSQL\17\bin;" + $env:Path
   
   # Connect without password (trust mode)
   psql -U postgres
   
   # In psql prompt, run:
   ALTER USER postgres PASSWORD 'newpassword123';
   \q
   ```

5. **Restore password authentication:**
   
   Open `pg_hba.conf` again and change `trust` back to `scram-sha-256`, then:
   ```powershell
   Restart-Service postgresql-x64-17
   ```

6. **Update `.env` file:**
   ```
   DB_PASSWORD=newpassword123
   ```

---

### Solution B: Use Windows Authentication (Alternative)

If you want to avoid password issues, you can use Windows authentication:

1. Edit `pg_hba.conf`:
   ```
   host    all             all             127.0.0.1/32            sspi
   ```

2. Update Django settings to use Windows auth (not recommended for production)

---

## Problem 2: Connect to pgAdmin 4

### Step 1: Install pgAdmin 4 (if not installed)

```powershell
# Using winget
winget install --id PostgreSQL.pgAdmin

# OR using chocolatey
choco install pgadmin4
```

### Step 2: Open pgAdmin 4

1. Launch pgAdmin 4 from Start Menu
2. You'll be asked to set a master password (for pgAdmin itself, not PostgreSQL)

### Step 3: Add Server Connection

1. **Right-click "Servers"** in the left panel
2. Click **"Register" → "Server..."**

3. **In the "General" tab:**
   - Name: `TCU_CEAA_Local`

4. **In the "Connection" tab:**
   - Host: `localhost`
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `postgres`
   - Password: `[your PostgreSQL password]`
   - ✅ Check "Save password"

5. Click **"Save"**

### Step 4: Access Your Database

1. Expand the server: `TCU_CEAA_Local`
2. Expand: `Databases`
3. Look for: `tcu_ceaa_db` (you need to create it first if it doesn't exist)

---

## Quick Commands Reference

### Create Database (after password is set):
```powershell
$env:Path = "C:\Program Files\PostgreSQL\17\bin;" + $env:Path
$env:PGPASSWORD = "your_new_password"
psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;"
```

### Test Connection:
```powershell
psql -U postgres -d tcu_ceaa_db
```

### Run Django Migrations:
```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py migrate
```

### Create Django Superuser:
```powershell
python manage.py createsuperuser
```

---

## Troubleshooting

### "Login failed" in Django
- ✅ Database exists: `tcu_ceaa_db`
- ✅ Migrations ran: `python manage.py migrate`
- ✅ User created: `python manage.py createsuperuser`
- ✅ Correct password in `.env` file

### Can't connect in pgAdmin 4
- Check PostgreSQL service is running
- Verify port 5432 in pgAdmin settings
- Make sure you're using the correct password
- Try `localhost` or `127.0.0.1` as host

### "Password authentication failed"
- Password in `.env` doesn't match PostgreSQL
- Follow Solution A above to reset password

---

## What to Do Now:

**Choose your path:**

### Path 1: Reset Password (Recommended)
1. Follow "Solution A" above to reset PostgreSQL password
2. Update `backend\.env` with new password
3. Create database: `psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;"`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`

### Path 2: I'll Help You Step-by-Step
Just tell me: **"I'm ready to reset the password"** and I'll guide you through each step.

Which path do you prefer?
