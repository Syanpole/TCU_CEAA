# Fresh PostgreSQL Setup with New Password
# Run this as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fresh PostgreSQL Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`n⚠️  This script needs Administrator privileges!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "✓ Running as Administrator`n" -ForegroundColor Green

# Define new simple password
$NEW_PASSWORD = "admin123"
$DB_NAME = "tcu_ceaa_db"

$pgVersion = "17"
$pgBinPath = "C:\Program Files\PostgreSQL\$pgVersion\bin"
$pgDataPath = "C:\Program Files\PostgreSQL\$pgVersion\data"
$pgHbaConf = "$pgDataPath\pg_hba.conf"
$serviceName = "postgresql-x64-$pgVersion"

Write-Host "New Password will be: $NEW_PASSWORD" -ForegroundColor Yellow
Write-Host "Database: $DB_NAME`n" -ForegroundColor Yellow

# Step 1: Stop PostgreSQL
Write-Host "Step 1: Stopping PostgreSQL service..." -ForegroundColor Cyan
try {
    Stop-Service -Name $serviceName -Force -ErrorAction Stop
    Start-Sleep -Seconds 3
    Write-Host "✓ PostgreSQL stopped`n" -ForegroundColor Green
} catch {
    Write-Host "✗ Could not stop service: $_`n" -ForegroundColor Red
    exit
}

# Step 2: Backup and modify pg_hba.conf to use 'trust'
Write-Host "Step 2: Temporarily enabling trust authentication..." -ForegroundColor Cyan
$backupPath = "$pgHbaConf.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $pgHbaConf -Destination $backupPath -Force
Write-Host "✓ Backup created: $backupPath" -ForegroundColor Green

# Read original pg_hba.conf and replace authentication method
$originalContent = Get-Content $pgHbaConf
$trustContent = $originalContent | ForEach-Object {
    if ($_ -match "^host\s+" -and -not ($_ -match "^#")) {
        $_ -replace "(scram-sha-256|md5|password)", "trust"
    } else {
        $_
    }
}

$trustContent | Set-Content -Path $pgHbaConf -Force
Write-Host "✓ Trust authentication enabled`n" -ForegroundColor Green

# Step 3: Start PostgreSQL
Write-Host "Step 3: Starting PostgreSQL service..." -ForegroundColor Cyan
Start-Service -Name $serviceName
Start-Sleep -Seconds 5
Write-Host "✓ PostgreSQL started`n" -ForegroundColor Green

# Step 4: Set new password
Write-Host "Step 4: Setting new password to '$NEW_PASSWORD'..." -ForegroundColor Cyan
$env:PGPASSWORD = $null
& "$pgBinPath\psql.exe" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD '$NEW_PASSWORD';" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Password set successfully`n" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to set password`n" -ForegroundColor Red
}

# Step 5: Ensure database exists
Write-Host "Step 5: Checking database '$DB_NAME'..." -ForegroundColor Cyan
$checkDB = & "$pgBinPath\psql.exe" -U postgres -h localhost -t -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>&1

if ($checkDB -match "1") {
    Write-Host "✓ Database '$DB_NAME' already exists`n" -ForegroundColor Green
} else {
    Write-Host "Creating database '$DB_NAME'..." -ForegroundColor Yellow
    & "$pgBinPath\psql.exe" -U postgres -h localhost -c "CREATE DATABASE $DB_NAME;" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database '$DB_NAME' created`n" -ForegroundColor Green
    }
}

# Step 6: Restore pg_hba.conf to use scram-sha-256
Write-Host "Step 6: Restoring secure authentication..." -ForegroundColor Cyan
$secureContent = $originalContent | ForEach-Object {
    if ($_ -match "^host\s+" -and -not ($_ -match "^#")) {
        # Ensure it uses scram-sha-256
        if ($_ -match "trust$") {
            $_ -replace "trust$", "scram-sha-256"
        } elseif ($_ -match "md5$") {
            $_ -replace "md5$", "scram-sha-256"
        } else {
            $_
        }
    } else {
        $_
    }
}

$secureContent | Set-Content -Path $pgHbaConf -Force
Write-Host "✓ Secure authentication restored`n" -ForegroundColor Green

# Step 7: Restart PostgreSQL
Write-Host "Step 7: Restarting PostgreSQL..." -ForegroundColor Cyan
Restart-Service -Name $serviceName -Force
Start-Sleep -Seconds 5
Write-Host "✓ PostgreSQL restarted`n" -ForegroundColor Green

# Step 8: Test connection with new password
Write-Host "Step 8: Testing connection with new password..." -ForegroundColor Cyan
$env:PGPASSWORD = $NEW_PASSWORD
$testResult = & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d $DB_NAME -c "SELECT version();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Connection test SUCCESSFUL!`n" -ForegroundColor Green
    
    # Step 9: Update .env file
    Write-Host "Step 9: Updating .env file..." -ForegroundColor Cyan
    $envPath = "C:\xampp\htdocs\TCU_CEAA\backend\.env"
    
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath
        $newEnvContent = $envContent | ForEach-Object {
            if ($_ -match "^DB_PASSWORD=") {
                "DB_PASSWORD=$NEW_PASSWORD"
            } else {
                $_
            }
        }
        $newEnvContent | Set-Content -Path $envPath -Force
        Write-Host "✓ .env file updated`n" -ForegroundColor Green
    }
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Setup Complete" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    Write-Host "`n📋 pgAdmin Connection Details:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "Host:     127.0.0.1" -ForegroundColor White
    Write-Host "Port:     5432" -ForegroundColor White
    Write-Host "Database: $DB_NAME" -ForegroundColor White
    Write-Host "Username: postgres" -ForegroundColor White
    Write-Host "Password: $NEW_PASSWORD" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    Write-Host "`n📝 Steps for pgAdmin:" -ForegroundColor Cyan
    Write-Host "1. Open pgAdmin" -ForegroundColor White
    Write-Host "2. Right-click 'Servers' → 'Register' → 'Server'" -ForegroundColor White
    Write-Host "3. General Tab:" -ForegroundColor White
    Write-Host "   - Name: TCU_CEAA_DB" -ForegroundColor Gray
    Write-Host "4. Connection Tab:" -ForegroundColor White
    Write-Host "   - Host: 127.0.0.1" -ForegroundColor Gray
    Write-Host "   - Port: 5432" -ForegroundColor Gray
    Write-Host "   - Database: $DB_NAME" -ForegroundColor Gray
    Write-Host "   - Username: postgres" -ForegroundColor Gray
    Write-Host "   - Password: $NEW_PASSWORD" -ForegroundColor Yellow
    Write-Host "   - ☑ Save password" -ForegroundColor Gray
    Write-Host "5. Click 'Save'`n" -ForegroundColor White
    
} else {
    Write-Host "✗ Connection test FAILED" -ForegroundColor Red
    Write-Host "Error: $testResult`n" -ForegroundColor Red
    
    Write-Host "Showing pg_hba.conf configuration:" -ForegroundColor Yellow
    Get-Content $pgHbaConf | Select-String "^host" | ForEach-Object { Write-Host $_ }
}

$env:PGPASSWORD = $null

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
