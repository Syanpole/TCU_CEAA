# PostgreSQL Password Fix Script
# This script will reset your PostgreSQL password and configure Django

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Password Fix for TCU_CEAA" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check which PostgreSQL version is running
$pg15 = Get-Service -Name postgresql-x64-15 -ErrorAction SilentlyContinue
$pg17 = Get-Service -Name postgresql-x64-17 -ErrorAction SilentlyContinue

Write-Host "Checking PostgreSQL services..." -ForegroundColor Yellow
if ($pg15 -and $pg15.Status -eq 'Running') {
    Write-Host "✓ PostgreSQL 15 is running" -ForegroundColor Green
    $pgVersion = "15"
    $serviceName = "postgresql-x64-15"
} elseif ($pg17 -and $pg17.Status -eq 'Running') {
    Write-Host "✓ PostgreSQL 17 is running" -ForegroundColor Green
    $pgVersion = "17"
    $serviceName = "postgresql-x64-17"
} else {
    Write-Host "✗ No PostgreSQL service is running!" -ForegroundColor Red
    Write-Host "Starting PostgreSQL 15..." -ForegroundColor Yellow
    Start-Service postgresql-x64-15
    $pgVersion = "15"
    $serviceName = "postgresql-x64-15"
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "Step 1: Configuring PostgreSQL for password reset..." -ForegroundColor Yellow

# PostgreSQL config path
$pgDataPath = "C:\Program Files\PostgreSQL\$pgVersion\data"
$pgBinPath = "C:\Program Files\PostgreSQL\$pgVersion\bin"
$pgHbaFile = "$pgDataPath\pg_hba.conf"

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠ This script needs to run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Backup pg_hba.conf
Write-Host "Backing up pg_hba.conf..." -ForegroundColor Yellow
Copy-Item $pgHbaFile "$pgHbaFile.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force

# Temporarily allow connections without password
Write-Host "Temporarily disabling password authentication..." -ForegroundColor Yellow
(Get-Content $pgHbaFile) -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust' | Set-Content $pgHbaFile

# Restart PostgreSQL
Write-Host "Restarting PostgreSQL..." -ForegroundColor Yellow
Restart-Service $serviceName
Start-Sleep -Seconds 5

# Set new password
$newPassword = "postgres123"
Write-Host ""
Write-Host "Step 2: Setting new password..." -ForegroundColor Yellow

# Add PostgreSQL to PATH temporarily
$env:Path = "$pgBinPath;" + $env:Path

# Reset password
try {
    $result = & psql -U postgres -c "ALTER USER postgres PASSWORD '$newPassword';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Password changed successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to change password: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Error changing password: $_" -ForegroundColor Red
}

# Restore password authentication
Write-Host ""
Write-Host "Step 3: Re-enabling password authentication..." -ForegroundColor Yellow
(Get-Content $pgHbaFile) -replace 'trust', 'scram-sha-256' | Set-Content $pgHbaFile

# Restart again
Write-Host "Restarting PostgreSQL..." -ForegroundColor Yellow
Restart-Service $serviceName
Start-Sleep -Seconds 5

# Create database if it doesn't exist
Write-Host ""
Write-Host "Step 4: Creating database..." -ForegroundColor Yellow
$env:PGPASSWORD = $newPassword
try {
    $dbExists = & psql -U postgres -lqt 2>&1 | Select-String -Pattern "tcu_ceaa_db"
    if (-not $dbExists) {
        Write-Host "Creating tcu_ceaa_db database..." -ForegroundColor Yellow
        & psql -U postgres -c "CREATE DATABASE tcu_ceaa_db;" 2>&1 | Out-Null
        Write-Host "✓ Database created!" -ForegroundColor Green
    } else {
        Write-Host "✓ Database already exists" -ForegroundColor Green
    }
} catch {
    Write-Host "Note: Database may already exist" -ForegroundColor Yellow
}

# Create .env file
Write-Host ""
Write-Host "Step 5: Creating .env file..." -ForegroundColor Yellow

$envContent = @"
# Database Configuration
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=$newPassword
DB_HOST=localhost
DB_PORT=5432

# Django Secret Key (generate a new one for production)
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production

# Debug mode (set to False in production)
DEBUG=True

# Allowed hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
"@

$envPath = "c:\xampp\htdocs\TCU_CEAA\backend\.env"
Set-Content -Path $envPath -Value $envContent -Force
Write-Host "✓ .env file created at: $envPath" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "✓ PostgreSQL Configuration Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database Credentials:" -ForegroundColor Yellow
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host "  Database: tcu_ceaa_db" -ForegroundColor White
Write-Host "  User: postgres" -ForegroundColor White
Write-Host "  Password: $newPassword" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run migrations:" -ForegroundColor White
Write-Host "     cd c:\xampp\htdocs\TCU_CEAA\backend" -ForegroundColor Cyan
Write-Host "     python manage.py migrate" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Create superuser:" -ForegroundColor White
Write-Host "     python manage.py createsuperuser" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Start Django server:" -ForegroundColor White
Write-Host "     python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "PostgreSQL Version: $pgVersion" -ForegroundColor Gray
Write-Host ""
