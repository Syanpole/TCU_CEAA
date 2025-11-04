# 🔗 CONNECT pgAdmin4 to Django Database - COMPLETE GUIDE

## ✅ CONFIRMED WORKING CREDENTIALS

| Setting | Value |
|---------|-------|
| **Password** | `admin123` ✓ |
| **Database** | `tcu_ceaa_db` ✓ |
| **User** | `postgres` |
| **Host** | `localhost` or `127.0.0.1` |
| **Port** | `5432` |

---

## 🎯 STEP-BY-STEP: View Database in pgAdmin4

### Step 1: Open pgAdmin4
- Launch pgAdmin4 application
- Enter master password if prompted

### Step 2: Ensure Server is Connected
Look at the left sidebar:
```
📂 Servers
  └── 🖥️ PostgreSQL XX (there may be a ⚡ icon if connected)
```

If **NOT connected**:
1. Right-click on **"PostgreSQL XX"**
2. Click **"Connect Server"**
3. Enter password: **`admin123`**
4. ✅ Check **"Save Password"**
5. Click **OK**

### Step 3: Refresh Databases
1. Click to expand **"PostgreSQL XX"** server
2. Find **"Databases"** folder
3. **Right-click** on "Databases"
4. Select **"Refresh"** (or press F5)

### Step 4: Your Database Should Appear!
```
📂 Servers
  └── 🖥️ PostgreSQL XX
      └── 📂 Databases
          ├── 📊 postgres (system database)
          └── 📊 tcu_ceaa_db ← YOUR APP DATABASE ✨
```

---

## 🔧 If Database is NOT Visible

### Quick Fix #1: Force Refresh
```
1. Right-click on "Databases" → Refresh
2. Right-click on "PostgreSQL XX" server → Disconnect
3. Right-click again → Connect Server
4. Enter password: admin123
5. Databases should now appear!
```

### Quick Fix #2: Verify Database Exists
Run this command in PowerShell:
```powershell
cd c:\xampp\htdocs\TCU_CEAA
python create_database.py
```

You should see:
```
✓ Database 'tcu_ceaa_db' already exists!
```

---

## 📊 What to See After Migrations

### Run Migrations First
```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py migrate
```

### Then in pgAdmin4
Navigate to:
```
tcu_ceaa_db
  → Schemas
      → public
          → Tables (Right-click → Refresh)
```

You'll see Django tables:
- `auth_user`
- `django_migrations`
- `myapp_customuser`
- `myapp_application`
- `myapp_grade`
- And more...

---

## 💡 How Django and pgAdmin4 Are Connected

### Same Database, Two Interfaces!

```
┌─────────────────────────────────────┐
│     PostgreSQL Server               │
│     (Running on localhost:5432)     │
│                                     │
│     Database: tcu_ceaa_db          │
│     ├── Tables                      │
│     ├── Data                        │
│     └── Schema                      │
└─────────────────────────────────────┘
           ▲              ▲
           │              │
           │              │
    ┌──────┴──────┐  ┌───┴─────┐
    │   Django    │  │ pgAdmin4│
    │   Backend   │  │         │
    └─────────────┘  └─────────┘
    
    Both use password: admin123
    Both connect to: tcu_ceaa_db
```

**Changes in Django = Changes in pgAdmin4**
- Add data in Django → See it in pgAdmin4
- Edit in pgAdmin4 → Django sees the changes
- **They're the same database!**

---

## 🚀 Complete Setup Workflow

### 1. Ensure PostgreSQL is Running
```powershell
Get-Service postgresql*
# Should show "Running" status
```

### 2. Verify Database Exists
```powershell
cd c:\xampp\htdocs\TCU_CEAA
python create_database.py
```

### 3. Update Django Database
```powershell
cd backend
python manage.py migrate
```

### 4. Refresh pgAdmin4
- Right-click "Databases" → Refresh
- Expand tcu_ceaa_db → Schemas → public → Tables
- Right-click "Tables" → Refresh

### 5. View Your Data
- Right-click any table
- Select "View/Edit Data" → "All Rows"

---

## 🎯 Test Database Connection

### Test in pgAdmin4
1. Right-click on `tcu_ceaa_db`
2. Select "Query Tool"
3. Run this SQL:
```sql
-- Create a test table
CREATE TABLE IF NOT EXISTS test_connection (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert test data
INSERT INTO test_connection (message) VALUES ('pgAdmin4 is connected!');

-- View the data
SELECT * FROM test_connection;
```

### Test from Django
```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py shell
```

Then in the Python shell:
```python
from django.db import connection

# Test connection
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
    
# Should print PostgreSQL version - SUCCESS!
```

---

## ✅ Verification Checklist

After setup, you should have:

- [ ] PostgreSQL service is running
- [ ] pgAdmin4 connected with password `admin123`
- [ ] Database `tcu_ceaa_db` visible in pgAdmin4
- [ ] Django migrations completed (`python manage.py migrate`)
- [ ] Tables visible under: tcu_ceaa_db → Schemas → public → Tables
- [ ] Can view table data in pgAdmin4
- [ ] Django server runs without errors (`python manage.py runserver`)

---

## 🆘 Common Issues & Solutions

### Issue: "Database does not exist"
**Solution:**
```powershell
python create_database.py
# Then refresh pgAdmin4
```

### Issue: "Password authentication failed"
**Solution:**
Make sure both files use `admin123`:
- `backend\.env` → `DB_PASSWORD=admin123`
- pgAdmin4 → Use `admin123` when connecting

### Issue: "Could not connect to server"
**Solution:**
```powershell
# Check PostgreSQL is running
Get-Service postgresql*

# Start if stopped
Start-Service postgresql-x64-18  # or your version
```

### Issue: Database visible but no tables
**Solution:**
```powershell
# Run Django migrations
cd backend
python manage.py migrate

# Then refresh Tables in pgAdmin4
```

---

## 🎉 SUCCESS INDICATORS

You know everything is working when:

1. ✅ pgAdmin4 shows `tcu_ceaa_db` database
2. ✅ Tables appear under public schema
3. ✅ Django server starts without database errors
4. ✅ You can run `python manage.py check --database default` successfully
5. ✅ Both pgAdmin4 and Django show the same data

**Your system and database are now fully synchronized!** 🚀

---

## 📝 Quick Reference Commands

```powershell
# Check database exists
python create_database.py

# Django migrations
cd backend
python manage.py migrate

# Django server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Django shell (test queries)
python manage.py shell
```

**Remember:** pgAdmin4 and Django are just two different ways to view/manage the **same database**. They're automatically connected once you use the same credentials!
