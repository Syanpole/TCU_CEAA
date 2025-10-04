# ✅ You're Connected to pgAdmin 4! Now Connect Django

I can see you have pgAdmin 4 open and connected to `tcu_ceaa_db`. 

Now we need to make Django use the same connection.

## 🔐 Step 1: Get Your PostgreSQL Password

Since you're already connected in pgAdmin 4, you know the password. 

**To see saved password in pgAdmin 4:**
1. Right-click on the `tcu_ceaa_db` server in pgAdmin
2. Click "Properties"
3. Go to "Connection" tab
4. The password should be saved there (or you remember it)

## ✏️ Step 2: Update Django .env File

Edit this file: `c:\xampp\htdocs\TCU_CEAA\backend\.env`

Update line 3 with your actual PostgreSQL password:

**Before:**
```env
DB_PASSWORD=your_password_here
```

**After:**
```env
DB_PASSWORD=your_actual_postgresql_password
```

Save the file (Ctrl+S).

## 🗄️ Step 3: Check Database in pgAdmin 4

In pgAdmin 4, expand:
```
tcu_ceaa_db
  └─ Schemas
      └─ public
          └─ Tables
```

**If you see Django tables** (like `auth_user`, `myapp_customuser`, etc.):
- ✅ Migrations already ran! Skip to Step 5.

**If Tables folder is empty:**
- ⚠️ You need to run migrations (go to Step 4)

## 🚀 Step 4: Run Django Migrations

Open PowerShell and run:

```powershell
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py migrate
```

**Refresh pgAdmin 4** (right-click Tables → Refresh) to see the new tables.

## 👤 Step 5: Create Django Superuser

```powershell
python manage.py createsuperuser
```

Fill in:
- Username: `admin` (or whatever you prefer)
- Email: `admin@example.com`
- Password: (choose a strong password)
- Password confirmation: (same password)

## 🌐 Step 6: Test Django Login

```powershell
python manage.py runserver
```

Open browser and go to: **http://localhost:8000/admin**

Login with the superuser credentials you just created.

## 🎯 Verify Everything Works

### In pgAdmin 4:
1. Expand: `tcu_ceaa_db` → `Schemas` → `public` → `Tables`
2. You should see tables like:
   - `auth_user`
   - `myapp_customuser`
   - `django_session`
   - `django_migrations`
   - etc.

3. Right-click on `myapp_customuser` → `View/Edit Data` → `All Rows`
4. You should see your superuser account

### In Django Admin:
1. Go to: http://localhost:8000/admin
2. Login with your superuser credentials
3. You should see the admin dashboard

## 🔗 How to View/Edit Data in pgAdmin 4

### View Tables:
```
tcu_ceaa_db → Schemas → public → Tables
```

### View Data:
- Right-click any table → "View/Edit Data" → "All Rows"

### Run SQL Queries:
1. Click on `tcu_ceaa_db`
2. Click "Tools" → "Query Tool"
3. Write SQL queries:
   ```sql
   SELECT * FROM myapp_customuser;
   SELECT * FROM auth_user;
   ```

### Common Tables You'll Use:
- `myapp_customuser` - User accounts
- `myapp_grade` - Grades data (if exists)
- `myapp_document` - Documents (if exists)
- `django_session` - Active sessions
- `auth_permission` - Permissions
- `auth_group` - User groups

## 📊 Quick SQL Examples

### See all users:
```sql
SELECT id, username, email, first_name, last_name 
FROM myapp_customuser;
```

### Count users:
```sql
SELECT COUNT(*) FROM myapp_customuser;
```

### See recent records:
```sql
SELECT * FROM myapp_customuser 
ORDER BY date_joined DESC 
LIMIT 10;
```

## ⚠️ If Login Still Fails

1. **Check .env password is correct:**
   ```powershell
   cd c:\xampp\htdocs\TCU_CEAA\backend
   Get-Content .env | Select-String "DB_PASSWORD"
   ```

2. **Test connection manually:**
   ```powershell
   $env:Path = "C:\Program Files\PostgreSQL\17\bin;" + $env:Path
   psql -U postgres -d tcu_ceaa_db
   ```
   (Enter the password when prompted)

3. **If it works in psql but not Django:**
   - Make sure .env file is saved
   - Restart Django server
   - Check for typos in password

## 🎉 You're All Set!

Once you:
1. ✅ Update `.env` with correct password
2. ✅ Run `python manage.py migrate`
3. ✅ Create superuser with `python manage.py createsuperuser`
4. ✅ Start server with `python manage.py runserver`

You'll be able to:
- ✅ Login to Django admin
- ✅ View data in pgAdmin 4
- ✅ Run SQL queries
- ✅ Manage your database visually

---

## 🚀 Quick Start Commands

```powershell
# 1. Update .env file (use notepad or VS Code)
code c:\xampp\htdocs\TCU_CEAA\backend\.env

# 2. Run migrations
cd c:\xampp\htdocs\TCU_CEAA\backend
python manage.py migrate

# 3. Create superuser
python manage.py createsuperuser

# 4. Start server
python manage.py runserver
```

Then open: http://localhost:8000/admin

---

**Ready to proceed?** Just update the `.env` file with your PostgreSQL password and run the commands above!
