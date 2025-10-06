# Fresh PostgreSQL & pgAdmin Setup Guide

## Quick Setup (3 Steps)

### Step 1: Run the Setup Script
1. **Right-click** on PowerShell
2. Select **"Run as Administrator"**
3. Run this command:
   ```powershell
   cd C:\xampp\htdocs\TCU_CEAA
   .\setup_fresh_password.ps1
   ```

This will:
- ✅ Set a new simple password: **admin123**
- ✅ Configure PostgreSQL properly
- ✅ Update your .env file automatically
- ✅ Ensure database `tcu_ceaa_db` exists

---

### Step 2: Delete Old Server in pgAdmin
1. Open **pgAdmin**
2. Find your **PostgreSQL 17** server in the left sidebar
3. **Right-click** on it → Select **"Remove Server"**
4. Confirm deletion

---

### Step 3: Create New Server in pgAdmin
1. In pgAdmin, **right-click** "Servers"
2. Select **"Register" → "Server"**

**General Tab:**
- Name: `TCU_CEAA_DB` (or any name you like)

**Connection Tab:**
- Host name/address: `127.0.0.1`
- Port: `5432`
- Maintenance database: `tcu_ceaa_db`
- Username: `postgres`
- Password: `admin123`
- ☑ **Save password** (check this box!)

3. Click **"Save"**

---

## New Connection Details

```
Host:     127.0.0.1
Port:     5432
Database: tcu_ceaa_db
Username: postgres
Password: admin123
```

---

## What Changed

| Before | After |
|--------|-------|
| Password: postgre123 (not working) | Password: **admin123** (working) |
| .env file: manual update needed | .env file: auto-updated |
| Authentication: mixed | Authentication: scram-sha-256 |

---

## Verification

After setup, verify the connection works:

```powershell
$env:PGPASSWORD="admin123"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h 127.0.0.1 -d tcu_ceaa_db -c "SELECT current_database(), current_user;"
```

You should see:
```
 current_database | current_user
------------------+--------------
 tcu_ceaa_db      | postgres
```

---

## Django Integration

Your Django backend is automatically configured! The setup script updates `backend/.env` with the new password.

To start Django:
```powershell
cd backend
python manage.py migrate
python manage.py runserver
```

---

## Troubleshooting

### If pgAdmin still asks for password:
1. Close pgAdmin **completely**
2. Delete the server connection again
3. **Restart your computer** (clears all cached credentials)
4. Create the server connection again with password: `admin123`

### If you want a different password:
Edit line 23 in `setup_fresh_password.ps1`:
```powershell
$NEW_PASSWORD = "your_password_here"
```
Then run the script again.
