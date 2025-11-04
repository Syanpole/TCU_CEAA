# PostgreSQL Connection Fix Script for TCU_CEAA
# This script will help you fix the password authentication error

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Connection Fix for Django" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get the correct PostgreSQL password
Write-Host "[STEP 1] Password Configuration" -ForegroundColor Yellow
Write-Host "You successfully opened pgAdmin, which means PostgreSQL is running." -ForegroundColor Green
Write-Host ""
Write-Host "What password did you use to connect to pgAdmin?" -ForegroundColor White
Write-Host "Common passwords: postgres, admin, root, 123456, or custom password" -ForegroundColor Gray
Write-Host ""
$pgPassword = Read-Host "Enter your PostgreSQL password"

# Step 2: Test the connection
Write-Host ""
Write-Host "[STEP 2] Testing PostgreSQL Connection..." -ForegroundColor Yellow

$env:PGPASSWORD = $pgPassword
$testConnection = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "SELECT version();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Connection successful!" -ForegroundColor Green
} else {
    Write-Host "✗ Connection failed with this password." -ForegroundColor Red
    Write-Host "Please check your password and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To find your PostgreSQL password:" -ForegroundColor Cyan
    Write-Host "1. Open pgAdmin" -ForegroundColor White
    Write-Host "2. Right-click on PostgreSQL server -> Properties" -ForegroundColor White
    Write-Host "3. Check the password you saved" -ForegroundColor White
    exit 1
}

# Step 3: Update .env file
Write-Host ""
Write-Host "[STEP 3] Updating .env file..." -ForegroundColor Yellow

$envPath = "c:\xampp\htdocs\TCU_CEAA\backend\.env"
$envContent = Get-Content $envPath -Raw

# Update the password in .env file
$envContent = $envContent -replace 'DB_PASSWORD=.*', "DB_PASSWORD=$pgPassword"

# Save the updated content
Set-Content -Path $envPath -Value $envContent -NoNewline

Write-Host "✓ .env file updated successfully!" -ForegroundColor Green

# Step 4: Check if database exists
Write-Host ""
Write-Host "[STEP 4] Checking if database 'tcu_ceaa_db' exists..." -ForegroundColor Yellow

$dbExists = & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='tcu_ceaa_db';" 2>&1

if ($dbExists -eq "1") {
    Write-Host "✓ Database 'tcu_ceaa_db' exists!" -ForegroundColor Green
} else {
    Write-Host "⚠ Database 'tcu_ceaa_db' does not exist. Creating it..." -ForegroundColor Yellow
    & "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "CREATE DATABASE tcu_ceaa_db;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database 'tcu_ceaa_db' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create database. Please create it manually in pgAdmin." -ForegroundColor Red
    }
}

# Step 5: Test Django connection
Write-Host ""
Write-Host "[STEP 5] Testing Django connection..." -ForegroundColor Yellow
Write-Host "Running: python manage.py check --database default" -ForegroundColor Gray

Set-Location "c:\xampp\htdocs\TCU_CEAA\backend"

if (Test-Path "..\\.venv\Scripts\Activate.ps1") {
    & "..\\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ Virtual environment not found, using system Python" -ForegroundColor Yellow
}

$djangoCheck = python manage.py check --database default 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Django can connect to PostgreSQL!" -ForegroundColor Green
} else {
    Write-Host "✗ Django connection test failed:" -ForegroundColor Red
    Write-Host $djangoCheck -ForegroundColor Red
}

# Final summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration Updated:" -ForegroundColor Green
Write-Host "  Database: tcu_ceaa_db" -ForegroundColor White
Write-Host "  User: postgres" -ForegroundColor White
Write-Host "  Password: $('*' * $pgPassword.Length)" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run migrations: python manage.py migrate" -ForegroundColor White
Write-Host "2. Start server: python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "If you still get errors, make sure:" -ForegroundColor Cyan
Write-Host "  • PostgreSQL service is running" -ForegroundColor White
Write-Host "  • pgAdmin can connect with the same password" -ForegroundColor White
Write-Host "  • Firewall is not blocking port 5432" -ForegroundColor White
Write-Host ""

# Clean up
$env:PGPASSWORD = $null
