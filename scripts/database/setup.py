#!/usr/bin/env python
"""
Django setup and management script for TCU-CEAA project
Taguig City University City Educational Assistance Allowance
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def setup_django():
    """Setup Django project"""
    print("Setting up Django backend...")
    
    # Change to backend directory
    os.chdir('django-react-app/backend')
    
    # Install requirements
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Make migrations
    run_command("python manage.py makemigrations", "Creating database migrations")
    
    # Apply migrations
    run_command("python manage.py migrate", "Applying database migrations")
    
    # Create superuser (optional)
    print("\nTo create a superuser, run: python manage.py createsuperuser")
    
    print("\n✓ Django setup completed!")

def setup_react():
    """Setup React frontend"""
    print("\nSetting up React frontend...")
    
    # Change to frontend directory
    os.chdir('../frontend')
    
    # Install dependencies
    run_command("npm install", "Installing Node.js dependencies")
    
    print("\n✓ React setup completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "django":
            setup_django()
        elif sys.argv[1] == "react":
            setup_react()
        elif sys.argv[1] == "all":
            setup_django()
            setup_react()
        else:
            print("Usage: python setup.py [django|react|all]")
    else:
        print("Usage: python setup.py [django|react|all]")
