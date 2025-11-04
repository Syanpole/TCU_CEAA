# 🔧 PostgreSQL Password Authentication Fix

## The Problem
Django shows: `password authentication failed for user "postgres"`

This means the password in your `.env` file doesn't match your actual PostgreSQL password.

---

## ✅ Quick Fix (3 Steps)

### Step 1: Find Your Actual PostgreSQL Password

Since you can open pgAdmin, you know the password. Common passwords are:
- `postgres`
- `admin`
- `123456`
- `root`
- Or a custom password you set during installation

**To verify in pgAdmin:**
1. Open pgAdmin
2. Right-click on "PostgreSQL 16" server
3. Click "Properties"
4. Check saved password or re-enter it

---

### Step 2: Update the `.env` File

1. Open: `c:\xampp\htdocs\TCU_CEAA\backend\.env`

2. Find this line:
   ```
   DB_PASSWORD=postgres123
   ```

3. Replace with YOUR actual password:
   ```
   DB_PASSWORD=your_actual_password
   ```

**Example:** If your password is `admin`:
```env
DB_PASSWORD=admin
```

---

### Step 3: Test the Connection

Run these commands in PowerShell:

```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
.venv\Scripts\Activate.ps1
python manage.py check --database default
python manage.py migrate
python manage.py runserver
```

---

## 🚀 Automated Fix

Run this PowerShell script to automatically fix everything:

```powershell
cd c:\xampp\htdocs\TCU_CEAA
.\fix_postgres_connection.ps1
```

The script will:
1. Ask for your PostgreSQL password
2. Test the connection
3. Automatically update the `.env` file
4. Create database if needed
5. Verify Django can connect

---

## 🔍 Manual Verification

### Test PostgreSQL is Running:
```powershell
# Check if PostgreSQL service is running
Get-Service postgresql*
```

### Test Password Manually:
```powershell
# Try connecting with psql (replace 'your_password')
$env:PGPASSWORD="your_password"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "SELECT version();"
```

If successful, that's your correct password!

---

## 📋 Common Password Locations

Your PostgreSQL password might be stored in:

1. **pgAdmin saved servers** - Open pgAdmin and check
2. **Installation notes** - Check where you wrote it down
3. **Password file** - `%APPDATA%\postgresql\pgpass.conf`
4. **Default** - Often `postgres` if not changed

---

## 🔄 Reset PostgreSQL Password (If Forgotten)

If you forgot your password:

1. Open Command Prompt as Administrator

2. Navigate to PostgreSQL bin:
   ```cmd
   cd "C:\Program Files\PostgreSQL\16\bin"
   ```

3. Run:
   ```cmd
   psql -U postgres
   ```

4. If it asks for password and you don't know it, you need to:
   - Stop PostgreSQL service
   - Edit `pg_hba.conf` to use `trust` authentication temporarily
   - Restart service
   - Connect and change password
   - Restore `pg_hba.conf` to `md5` or `scram-sha-256`

**Easier option:** Reinstall PostgreSQL or use the password you set in pgAdmin.

---

## ✨ After Fix Checklist

- [ ] `.env` file has correct password
- [ ] PostgreSQL service is running
- [ ] pgAdmin can connect
- [ ] `python manage.py check --database default` works
- [ ] `python manage.py migrate` works
- [ ] `python manage.py runserver` starts without errors

---

## 🆘 Still Having Issues?

### Check PostgreSQL Service:
```powershell
# Check status
Get-Service postgresql*

# Start if stopped
Start-Service postgresql-x64-16
```

### Check Connection String:
Current configuration from `.env`:
- Database: `tcu_ceaa_db`
- User: `postgres`
- Password: (check your `.env` file)
- Host: `localhost`
- Port: `5432`

### Verify Database Exists:
```powershell
$env:PGPASSWORD="your_password"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -l
```

Look for `tcu_ceaa_db` in the list. If not there, create it:
```powershell
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE tcu_ceaa_db;"
```

---

## 💡 Pro Tip

Save your PostgreSQL password securely:
1. Use a password manager
2. Document it in a secure location
3. Use the same password in pgAdmin and `.env` file

**Never commit the `.env` file to Git!** (It should be in `.gitignore`)

---

## Success! ✅

Once fixed, you should see:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version X.X.X, using settings 'backend_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Your Django server is now running!** 🎉
