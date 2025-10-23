# Quick PostgreSQL Setup for TCU CEAA
# This script will help you complete the PostgreSQL setup

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TCU CEAA - PostgreSQL Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# PostgreSQL was just installed, add to PATH for this session
$env:Path += ";C:\Program Files\PostgreSQL\15\bin"

Write-Host "Step 1: Testing PostgreSQL installation..." -ForegroundColor Yellow
try {
    $pgVersion = & psql --version 2>&1
    Write-Host "✓ PostgreSQL installed: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ PostgreSQL not found in PATH. Please restart PowerShell." -ForegroundColor Red
    Write-Host "  Or manually add: C:\Program Files\PostgreSQL\15\bin to PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Database Configuration" -ForegroundColor Yellow
Write-Host ""

# Get PostgreSQL password
Write-Host "Enter the password for PostgreSQL 'postgres' user:" -ForegroundColor Cyan
Write-Host "(This was set during PostgreSQL installation)" -ForegroundColor Gray
$pgPassword = Read-Host "Password" -AsSecureString
$pgPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($pgPassword)
)

# Update .env file
Write-Host ""
Write-Host "Updating .env file..." -ForegroundColor Yellow
$envPath = "backend\.env"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $envContent = $envContent -replace 'DB_PASSWORD=.*', "DB_PASSWORD=$pgPasswordPlain"
    $envContent | Set-Content $envPath
    Write-Host "✓ .env file updated" -ForegroundColor Green
} else {
    Write-Host "✗ .env file not found at: $envPath" -ForegroundColor Red
    exit 1
}

# Set password for psql commands
$env:PGPASSWORD = $pgPasswordPlain

Write-Host ""
Write-Host "Step 3: Creating database 'tcu_ceaa_db'..." -ForegroundColor Yellow

try {
    # Check if database exists
    $dbCheck = & psql -U postgres -h localhost -lqt 2>&1 | Select-String "tcu_ceaa_db"
    
    if ($dbCheck) {
        Write-Host "Database 'tcu_ceaa_db' already exists!" -ForegroundColor Yellow
        $recreate = Read-Host "Do you want to drop and recreate it? (yes/no)"
        if ($recreate -eq "yes") {
            & psql -U postgres -h localhost -c "DROP DATABASE tcu_ceaa_db;" 2>&1 | Out-Null
            & psql -U postgres -h localhost -c "CREATE DATABASE tcu_ceaa_db;" 2>&1 | Out-Null
            Write-Host "✓ Database recreated" -ForegroundColor Green
        } else {
            Write-Host "✓ Using existing database" -ForegroundColor Green
        }
    } else {
        & psql -U postgres -h localhost -c "CREATE DATABASE tcu_ceaa_db;" 2>&1 | Out-Null
        Write-Host "✓ Database created successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Failed to create database: $_" -ForegroundColor Red
    Write-Host "  You may need to create it manually:" -ForegroundColor Yellow
    Write-Host "  psql -U postgres -c `"CREATE DATABASE tcu_ceaa_db;`"" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Step 4: Running Django migrations..." -ForegroundColor Yellow
Set-Location backend

try {
    python manage.py makemigrations
    python manage.py migrate
    Write-Host "✓ Migrations completed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Migration failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Create a superuser:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     python manage.py createsuperuser" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the Django server:" -ForegroundColor White
Write-Host "     python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "Database Info:" -ForegroundColor Cyan
Write-Host "  Database: tcu_ceaa_db" -ForegroundColor White
Write-Host "  User: postgres" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host ""

# Clean up password from environment
Remove-Variable env:PGPASSWORD -ErrorAction SilentlyContinue
