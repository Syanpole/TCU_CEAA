import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import CustomUser

# Create superuser
username = 'admin'
email = 'admin@tcu.edu.ph'
password = 'admin@123'

if not CustomUser.objects.filter(username=username).exists():
    user = CustomUser.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='admin',
        first_name='Admin',
        last_name='User'
    )
    print(f"Superuser '{username}' created successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
else:
    print(f"Superuser '{username}' already exists!")
    # Update the password
    user = CustomUser.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"Password updated for '{username}'!")
