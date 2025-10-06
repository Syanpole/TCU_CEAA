# Quick Fix - Manual PostgreSQL Password Reset

## The Problem:
Django can't connect to PostgreSQL because there's no `.env` file with the correct password.

## Quick Fix (Try This First):

### Option 1: Try Common Passwords

The PostgreSQL password might be one of these:
- `postgres`
- `admin`
- `root`
- (leave empty)

**Test it:**
```powershell
# Try connecting with 'postgres' as password
$env:PGPASSWORD = "postgres"
psql -U postgres -c "SELECT version();"
```

If that works, create the `.env` file:
```powershell
# Create .env file
$envContent = @"
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
"@

Set-Content -Path "c:\xampp\htdocs\TCU_CEAA\backend\.env" -Value $envContent
```

### Option 2: Reset Password (Requires Admin Rights)

If the common passwords don't work, run this PowerShell **AS ADMINISTRATOR**:

```powershell
# Run the automated fix script
cd c:\xampp\htdocs\TCU_CEAA
.\fix_postgresql_password.ps1
```

The script will:
1. ✓ Reset PostgreSQL password to `postgres123`
2. ✓ Create the `.env` file
3. ✓ Create the database
4. ✓ Configure everything for you

### Option 3: Manual Password Reset

If you prefer to do it manually:

1. **Edit pg_hba.conf** (requires admin):
   ```powershell
   notepad "C:\Program Files\PostgreSQL\15\data\pg_hba.conf"
   ```

2. **Find these lines:**
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

3. **Change to:**
   ```
   host    all             all             127.0.0.1/32            trust
   ```

4. **Restart PostgreSQL:**
   ```powershell
   Restart-Service postgresql-x64-15
   ```

5. **Change password:**
   ```powershell
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "ALTER USER postgres PASSWORD 'postgres123';"
   ```

6. **Change pg_hba.conf back to:**
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

7. **Restart again:**
   ```powershell
   Restart-Service postgresql-x64-15
   ```

8. **Create .env file:**
   ```powershell
   $envContent = @"
   DB_NAME=tcu_ceaa_db
   DB_USER=postgres
   DB_PASSWORD=postgres123
   DB_HOST=localhost
   DB_PORT=5432
   "@

   Set-Content -Path "c:\xampp\htdocs\TCU_CEAA\backend\.env" -Value $envContent
   ```

## After Fixing the Password:

1. **Create the database:**
   ```powershell
   $env:PGPASSWORD = "postgres123"
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE tcu_ceaa_db;"
   ```

2. **Run migrations:**
   ```powershell
   cd c:\xampp\htdocs\TCU_CEAA\backend
   python manage.py migrate
   ```

3. **Start Django:**
   ```powershell
   python manage.py runserver
   ```

## Troubleshooting:

### "Access denied" when editing pg_hba.conf
→ Run PowerShell as Administrator

### "Service not found"
→ Check your PostgreSQL version:
```powershell
Get-Service postgresql*
```

### "Database already exists"
→ That's fine! Just skip the CREATE DATABASE step

### Still getting password errors
→ Make sure the .env file is in: `c:\xampp\htdocs\TCU_CEAA\backend\.env`
