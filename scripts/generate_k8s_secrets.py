#!/usr/bin/env python3
"""
Generate Kubernetes Secrets from .env file
Reads backend/.env and creates k8s/staging/01-secrets.yaml with base64-encoded secrets
"""
import os
import base64
import sys

def read_env_file(env_path):
    """Parse .env file into a dictionary"""
    env_vars = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    env_vars[key] = value
    return env_vars

def to_base64(text):
    """Convert string to base64"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def generate_secrets_yaml(env_vars, environment='staging'):
    """Generate Kubernetes secrets YAML"""
    
    # Environment-specific values
    if environment == 'staging':
        namespace = 'tcu-ceaa-staging'
        db_name = 'tcu_ceaa_staging'
        bucket_name = 'tcu-ceaa-staging-media'
        allowed_hosts = 'staging.tcu-ceaa.com,api-staging.tcu-ceaa.com'
        frontend_url = 'http://staging.tcu-ceaa.com'
        cors_origins = 'http://staging.tcu-ceaa.com'
    else:
        namespace = 'tcu-ceaa'
        db_name = 'tcu_ceaa'
        bucket_name = 'tcu-ceaa-media'
        allowed_hosts = 'tcu-ceaa.com,api.tcu-ceaa.com'
        frontend_url = 'https://tcu-ceaa.com'
        cors_origins = 'https://tcu-ceaa.com,https://www.tcu-ceaa.com'
    
    # Base64 encode secrets
    secrets = {
        'POSTGRES_DB': to_base64(db_name),
        'POSTGRES_USER': to_base64('postgres'),
        'POSTGRES_PASSWORD': to_base64(env_vars['DB_PASSWORD']),
        'SECRET_KEY': to_base64(env_vars['SECRET_KEY']),
        'AWS_ACCESS_KEY_ID': to_base64(env_vars['AWS_ACCESS_KEY_ID']),
        'AWS_SECRET_ACCESS_KEY': to_base64(env_vars['AWS_SECRET_ACCESS_KEY']),
        'AWS_STORAGE_BUCKET_NAME': to_base64(bucket_name),
        'AWS_S3_REGION_NAME': to_base64(env_vars['AWS_S3_REGION_NAME']),
        'EMAIL_HOST_USER': to_base64(env_vars['EMAIL_HOST_USER']),
        'EMAIL_HOST_PASSWORD': to_base64(env_vars['EMAIL_HOST_PASSWORD']),
    }
    
    # Create YAML content
    yaml_content = f"""apiVersion: v1
kind: Secret
metadata:
  name: tcu-ceaa-secrets
  namespace: {namespace}
type: Opaque
data:
  # Database credentials
  POSTGRES_DB: {secrets['POSTGRES_DB']}
  POSTGRES_USER: {secrets['POSTGRES_USER']}
  POSTGRES_PASSWORD: {secrets['POSTGRES_PASSWORD']}
  
  # Django secret key
  SECRET_KEY: {secrets['SECRET_KEY']}
  
  # AWS credentials
  AWS_ACCESS_KEY_ID: {secrets['AWS_ACCESS_KEY_ID']}
  AWS_SECRET_ACCESS_KEY: {secrets['AWS_SECRET_ACCESS_KEY']}
  AWS_STORAGE_BUCKET_NAME: {secrets['AWS_STORAGE_BUCKET_NAME']}
  AWS_S3_REGION_NAME: {secrets['AWS_S3_REGION_NAME']}
  
  # Email credentials
  EMAIL_HOST_USER: {secrets['EMAIL_HOST_USER']}
  EMAIL_HOST_PASSWORD: {secrets['EMAIL_HOST_PASSWORD']}

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: tcu-ceaa-config
  namespace: {namespace}
data:
  # Django settings
  DEBUG: "False"
  ALLOWED_HOSTS: "{allowed_hosts}"
  
  # Database connection
  DATABASE_URL: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgres-service:5432/{db_name}"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  
  # Redis connection
  REDIS_URL: "redis://redis-service:6379/0"
  CELERY_BROKER_URL: "redis://redis-service:6379/0"
  CELERY_RESULT_BACKEND: "redis://redis-service:6379/0"
  
  # AWS/S3 settings
  USE_CLOUD_STORAGE: "True"
  USE_ADVANCED_OCR: "True"
  ADVANCED_OCR_REGION: "{env_vars['AWS_S3_REGION_NAME']}"
  OCR_CONFIDENCE_THRESHOLD: "80"
  
  # Email settings
  EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend"
  EMAIL_HOST: "smtp.gmail.com"
  EMAIL_PORT: "587"
  EMAIL_USE_TLS: "True"
  DEFAULT_FROM_EMAIL: "TCU-CEAA <noreply@tcu-ceaa.edu.ph>"
  
  # Frontend URL
  FRONTEND_URL: "{frontend_url}"
  CORS_ALLOWED_ORIGINS: "{cors_origins}"
  
  # Feature flags
  FEATURE_AUTO_VERIFY_COE: "{'True' if environment == 'staging' else 'True'}"
  FEATURE_AUTO_VERIFY_ID: "{'True' if environment == 'staging' else 'True'}"
  FEATURE_AUTO_VERIFY_BIRTH_CERT: "{'False' if environment == 'staging' else 'True'}"
  FEATURE_AUTO_VERIFY_VOTERS: "{'False' if environment == 'staging' else 'True'}"
  FEATURE_LIVENESS_CHECK: "{'False' if environment == 'staging' else 'True'}"
  
  # Security settings
  CSRF_COOKIE_SECURE: "{'False' if environment == 'staging' else 'True'}"
  SESSION_COOKIE_SECURE: "{'False' if environment == 'staging' else 'True'}"
  SECURE_SSL_REDIRECT: "{'False' if environment == 'staging' else 'True'}"
"""
    
    return yaml_content, namespace, db_name, bucket_name

def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else 'staging'
    
    print(f"🔐 Generating Kubernetes Secrets for {environment}")
    print()
    
    # Read .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
    if not os.path.exists(env_path):
        print(f"❌ .env file not found at: {env_path}")
        sys.exit(1)
    
    print(f"📄 Reading: {env_path}")
    env_vars = read_env_file(env_path)
    print(f"✅ Found {len(env_vars)} environment variables")
    print()
    
    # Validate required secrets
    required = ['DB_PASSWORD', 'SECRET_KEY', 'AWS_ACCESS_KEY_ID', 
                'AWS_SECRET_ACCESS_KEY', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD',
                'AWS_S3_REGION_NAME']
    
    missing = [key for key in required if key not in env_vars]
    if missing:
        print("❌ Missing required secrets:")
        for key in missing:
            print(f"   - {key}")
        sys.exit(1)
    
    print("✅ All required secrets found")
    print("🔄 Generating YAML with base64-encoded secrets...")
    print()
    
    # Generate YAML
    yaml_content, namespace, db_name, bucket_name = generate_secrets_yaml(env_vars, environment)
    
    # Write to file
    output_path = os.path.join(os.path.dirname(__file__), '..', 'k8s', environment, '01-secrets.yaml')
    with open(output_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Generated: {output_path}")
    print(f"   Namespace: {namespace}")
    print(f"   Database: {db_name}")
    print(f"   S3 Bucket: {bucket_name}")
    print()
    print("🔐 Secrets included:")
    print("   ✓ POSTGRES_PASSWORD")
    print("   ✓ SECRET_KEY")
    print("   ✓ AWS_ACCESS_KEY_ID")
    print("   ✓ AWS_SECRET_ACCESS_KEY")
    print("   ✓ EMAIL_HOST_USER")
    print("   ✓ EMAIL_HOST_PASSWORD")
    print()
    print("⚠️  SECURITY WARNING:")
    print("   - This file is in .gitignore (will not be committed)")
    print("   - Keep your .env file secure")
    print("   - Never share these credentials")
    print()
    print("📦 Next steps:")
    print(f"   1. Review: {output_path}")
    print(f"   2. Apply: kubectl apply -f {output_path}")
    print(f"   3. Verify: kubectl get secrets -n {namespace}")
    print()
    print("✨ Done!")

if __name__ == '__main__':
    main()
