# ============================================
# PostgreSQL Connection Guide for pgAdmin
# ============================================

## PASSWORD CONFIRMED: postgre123

## For pgAdmin 4 Connection:

### Server Connection Settings:
```
General Tab:
  Name: TCU_CEAA (or any name you prefer)

Connection Tab:
  Host name/address: 127.0.0.1
  Port: 5432
  Maintenance database: postgres
  Username: postgres
  Password: postgre123
  
  ☑ Save password (optional)
```

### Important Notes:
1. Use **127.0.0.1** instead of **localhost** if you have connection issues
2. The password is: **postgre123** (NOT postgres123)
3. If prompted for password multiple times, make sure to check "Save password"

## Troubleshooting:

### If you still can't connect in pgAdmin:
1. Close pgAdmin completely
2. Right-click on pgAdmin and "Run as Administrator"
3. Try connecting again with password: postgre123

### Alternative: Reset pgAdmin saved passwords
If pgAdmin is using a cached wrong password:
1. In pgAdmin, go to File → Preferences
2. Navigate to: Paths → Binary paths
3. Or delete saved passwords: File → Preferences → SQL Editor → Clear saved passwords

## Current Status:
✅ PostgreSQL 17 is running
✅ Password is set to: postgre123
✅ Database 'tcu_ceaa_db' exists
✅ Command-line connection works
✅ Django .env file is correctly configured

## Django Database Status:
✅ Connection working
⚠️  Needs migration: Run `python manage.py migrate`

## Quick Test Command:
Run this in PowerShell to verify connection:
```powershell
$env:PGPASSWORD="postgre123"; & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d tcu_ceaa_db -c "SELECT version();"
```

If this works but pgAdmin doesn't, the issue is with pgAdmin's cached credentials.
