# 🔐 Password Management Guide

## Quick Commands

### 1. **Interactive Password Manager** (Recommended)
```bash
cd backend
python manage_passwords.py
```

This gives you a menu with options:
- List all users
- Change password for any user
- Admin reset (no old password needed)
- Create new user

---

## 2. **Django Shell Method** (Manual)

### Change Password for Current User
```bash
cd backend
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Find the user
user = User.objects.get(username='your_username')

# Change password
user.set_password('new_password_here')
user.save()

print(f"✅ Password changed for {user.username}")
```

### Change Password by User ID
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Find by ID
user = User.objects.get(id=1)

# Change password
user.set_password('new_password_here')
user.save()

print(f"✅ Password changed for {user.username}")
```

### List All Users
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# List all users
for user in User.objects.all():
    print(f"ID: {user.id} | Username: {user.username} | Role: {user.role}")
```

---

## 3. **Django Admin Command** (One-liner)

### Change Password
```bash
cd backend
python manage.py changepassword username_here
```

This will prompt you for a new password interactively.

---

## 4. **Create Admin User**
```bash
cd backend
python manage.py createsuperuser
```

---

## 🔒 Security Notes

### ✅ What Django Does Automatically:
- **Hashes passwords** using PBKDF2-SHA256
- **Salts passwords** (adds random data before hashing)
- **Never stores plain text** passwords
- **Validates password strength**

### ⚠️ Password Storage Example:
```
Plain text:      "mypassword123"
Stored in DB:    "pbkdf2_sha256$600000$abc123$hash..."
                  └── Algorithm  └─ Iterations └─ Salt └─ Hash
```

### 🚫 Never Do This:
```python
# ❌ WRONG - Don't set password directly!
user.password = 'newpassword'  # This stores plain text!
user.save()

# ✅ CORRECT - Use set_password()
user.set_password('newpassword')  # This hashes it
user.save()
```

---

## 📊 Check Current Users

```bash
cd backend
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('\n'.join([f'{u.username} - {u.role}' for u in User.objects.all()]))"
```

---

## 🎯 Quick Examples

### Reset Admin Password
```bash
cd backend
python manage_passwords.py
# Choose option 3 (Admin reset)
# Enter username: admin
# Enter new password
```

### Create New Student User
```bash
cd backend
python manage_passwords.py
# Choose option 4 (Create user)
# Follow prompts
```

### Change Your Own Password
```bash
cd backend
python manage.py changepassword your_username
```

---

## 🔐 Production Best Practices

1. **Never share passwords** - Each user should have their own
2. **Use strong passwords** - At least 12 characters, mixed case, numbers, symbols
3. **Rotate admin passwords** regularly
4. **Never commit passwords** to git
5. **Use environment variables** for sensitive data
6. **Enable 2FA** (Two-Factor Authentication) for admin accounts

---

## 🆘 Emergency: Reset All Passwords

If you need to reset all passwords (security breach):

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Force password reset for all users
for user in User.objects.all():
    user.set_password(f"TempPass{user.id}2024!")
    user.save()
    print(f"Reset password for {user.username}")
```

Then notify all users to change their passwords immediately.
