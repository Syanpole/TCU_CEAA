# TCU CEAA - GCP Setup Script
# Run this script to set up your GCP project for production deployment

# Configuration Variables
$PROJECT_ID = "tcu-ceaa-prod"
$PROJECT_NAME = "TCU CEAA Production"
$REGION = "asia-southeast1"
$ZONE = "asia-southeast1-a"
$SQL_INSTANCE_NAME = "tcu-ceaa-db-prod"
$REPO_NAME = "tcu-ceaa-images"
$BUCKET_NAME = "tcu-ceaa-documents-prod"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "TCU CEAA - GCP Production Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    gcloud version | Out-Null
    Write-Host "✓ Google Cloud SDK is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ Google Cloud SDK not found. Please install it first." -ForegroundColor Red
    Write-Host "  Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Login to GCP
Write-Host "`nStep 1: Authenticating with Google Cloud..." -ForegroundColor Yellow
gcloud auth login

# Create Project
Write-Host "`nStep 2: Creating GCP Project..." -ForegroundColor Yellow
gcloud projects create $PROJECT_ID --name="$PROJECT_NAME" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Project created: $PROJECT_ID" -ForegroundColor Green
} else {
    Write-Host "! Project may already exist" -ForegroundColor Yellow
}

# Set active project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Link billing account
Write-Host "`nStep 3: Billing Account Setup" -ForegroundColor Yellow
Write-Host "Available billing accounts:" -ForegroundColor Cyan
gcloud billing accounts list
Write-Host "`nEnter your Billing Account ID: " -ForegroundColor Yellow -NoNewline
$BILLING_ACCOUNT_ID = Read-Host

if ($BILLING_ACCOUNT_ID) {
    gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
    Write-Host "✓ Billing account linked" -ForegroundColor Green
} else {
    Write-Host "! Skipping billing setup" -ForegroundColor Yellow
}

# Enable APIs
Write-Host "`nStep 4: Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "run.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "cloudbuild.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -NoNewline
    gcloud services enable $api --quiet
    Write-Host " ✓" -ForegroundColor Green
}

# Create Cloud SQL Instance
Write-Host "`nStep 5: Creating Cloud SQL PostgreSQL Instance..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes..." -ForegroundColor Cyan

gcloud sql instances create $SQL_INSTANCE_NAME `
    --database-version=POSTGRES_15 `
    --tier=db-f1-micro `
    --region=$REGION `
    --backup `
    --backup-start-time=03:00 `
    --enable-bin-log `
    --maintenance-window-day=SUN `
    --maintenance-window-hour=04 `
    --database-flags=max_connections=100 `
    --quiet 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Cloud SQL instance created" -ForegroundColor Green
} else {
    Write-Host "! Instance may already exist" -ForegroundColor Yellow
}

# Generate strong password
$DB_PASSWORD = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Create database and user
Write-Host "`nStep 6: Setting up database..." -ForegroundColor Yellow
gcloud sql databases create tcu_ceaa --instance=$SQL_INSTANCE_NAME --quiet 2>$null
gcloud sql users create tcu_admin --instance=$SQL_INSTANCE_NAME --password="$DB_PASSWORD" --quiet 2>$null

$SQL_CONNECTION_NAME = gcloud sql instances describe $SQL_INSTANCE_NAME --format="value(connectionName)"
Write-Host "✓ Database created" -ForegroundColor Green
Write-Host "  Connection Name: $SQL_CONNECTION_NAME" -ForegroundColor Cyan
Write-Host "  Database Password: $DB_PASSWORD" -ForegroundColor Cyan
Write-Host "  ⚠️  SAVE THESE CREDENTIALS SECURELY!" -ForegroundColor Red

# Create Artifact Registry
Write-Host "`nStep 7: Creating Artifact Registry..." -ForegroundColor Yellow
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="TCU CEAA Docker images" `
    --quiet 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Artifact Registry created" -ForegroundColor Green
} else {
    Write-Host "! Repository may already exist" -ForegroundColor Yellow
}

# Configure Docker auth
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# Generate Django secret key
$DJANGO_SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object {[char]$_})

# Create secrets
Write-Host "`nStep 8: Creating secrets in Secret Manager..." -ForegroundColor Yellow

Write-Host "Enter your AWS Access Key ID: " -ForegroundColor Yellow -NoNewline
$AWS_ACCESS_KEY = Read-Host
Write-Host "Enter your AWS Secret Access Key: " -ForegroundColor Yellow -NoNewline
$AWS_SECRET_KEY = Read-Host -AsSecureString
$AWS_SECRET_KEY = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($AWS_SECRET_KEY))
Write-Host "Enter your AWS S3 Bucket Name: " -ForegroundColor Yellow -NoNewline
$AWS_BUCKET = Read-Host
Write-Host "Enter your AWS Cognito Identity Pool ID: " -ForegroundColor Yellow -NoNewline
$AWS_COGNITO_POOL = Read-Host

# Create secrets
echo $DB_PASSWORD | gcloud secrets create DB_PASSWORD --data-file=- --quiet 2>$null
echo $DJANGO_SECRET_KEY | gcloud secrets create DJANGO_SECRET_KEY --data-file=- --quiet 2>$null
echo $AWS_ACCESS_KEY | gcloud secrets create AWS_ACCESS_KEY_ID --data-file=- --quiet 2>$null
echo $AWS_SECRET_KEY | gcloud secrets create AWS_SECRET_ACCESS_KEY --data-file=- --quiet 2>$null
echo $AWS_BUCKET | gcloud secrets create AWS_STORAGE_BUCKET_NAME --data-file=- --quiet 2>$null
echo $AWS_COGNITO_POOL | gcloud secrets create AWS_COGNITO_IDENTITY_POOL_ID --data-file=- --quiet 2>$null

Write-Host "✓ Secrets created" -ForegroundColor Green

# Grant access to secrets
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$SERVICE_ACCOUNT = "$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

$secrets = @("DB_PASSWORD", "DJANGO_SECRET_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_STORAGE_BUCKET_NAME", "AWS_COGNITO_IDENTITY_POOL_ID")
foreach ($secret in $secrets) {
    gcloud secrets add-iam-policy-binding $secret `
        --member="serviceAccount:$SERVICE_ACCOUNT" `
        --role="roles/secretmanager.secretAccessor" `
        --quiet 2>$null
}

# Save configuration
Write-Host "`nStep 9: Saving configuration..." -ForegroundColor Yellow
$config = @"
# TCU CEAA GCP Configuration
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

PROJECT_ID=$PROJECT_ID
REGION=$REGION
SQL_CONNECTION_NAME=$SQL_CONNECTION_NAME
DB_PASSWORD=$DB_PASSWORD
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
AWS_BUCKET=$AWS_BUCKET
ARTIFACT_REGISTRY=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}
"@

$config | Out-File -FilePath "gcp-config.txt" -Encoding UTF8
Write-Host "✓ Configuration saved to gcp-config.txt" -ForegroundColor Green

# Summary
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Review gcp-config.txt for your credentials" -ForegroundColor White
Write-Host "2. Run setup-aws.ps1 to configure AWS services" -ForegroundColor White
Write-Host "3. Run deploy.ps1 to build and deploy your application" -ForegroundColor White
Write-Host "`n⚠️  Keep gcp-config.txt secure and do not commit to git!" -ForegroundColor Red
