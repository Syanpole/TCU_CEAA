# Complete PostgreSQL Password Reset
# This script will reset the postgres user password to 'postgres123'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Password Reset" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pgDataPath = "C:\Program Files\PostgreSQL\15\data"
$pgHbaPath = "$pgDataPath\pg_hba.conf"
$pgHbaBackup = "$pgDataPath\pg_hba.conf.backup"

# Step 1: Backup pg_hba.conf
Write-Host "Step 1: Backing up pg_hba.conf..." -ForegroundColor Yellow
try {
    Copy-Item -Path $pgHbaPath -Destination $pgHbaBackup -Force
    Write-Host "[OK] Backup created" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to backup: $_" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator!" -ForegroundColor Yellow
    exit 1
}

# Step 2: Modify pg_hba.conf to use 'trust' authentication
Write-Host ""
Write-Host "Step 2: Modifying pg_hba.conf to allow passwordless connection..." -ForegroundColor Yellow
try {
    $content = Get-Content $pgHbaPath
    $newContent = $content -replace 'host\s+all\s+all\s+127\.0\.0\.1/32\s+scram-sha-256', 'host    all             all             127.0.0.1/32            trust'
    $newContent = $newContent -replace 'host\s+all\s+all\s+::1/128\s+scram-sha-256', 'host    all             all             ::1/128                 trust'
    $newContent = $newContent -replace 'host\s+all\s+all\s+127\.0\.0\.1/32\s+md5', 'host    all             all             127.0.0.1/32            trust'
    $newContent = $newContent -replace 'host\s+all\s+all\s+::1/128\s+md5', 'host    all             all             ::1/128                 trust'
    $newContent | Set-Content $pgHbaPath
    Write-Host "[OK] pg_hba.conf modified" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to modify pg_hba.conf: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Restart PostgreSQL service
Write-Host ""
Write-Host "Step 3: Restarting PostgreSQL service..." -ForegroundColor Yellow
try {
    Restart-Service postgresql-x64-15
    Start-Sleep -Seconds 3
    Write-Host "[OK] Service restarted" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to restart service: $_" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator!" -ForegroundColor Yellow
    exit 1
}

# Step 4: Reset password
Write-Host ""
Write-Host "Step 4: Resetting password to 'postgres123'..." -ForegroundColor Yellow
try {
    $result = & 'C:\Program Files\PostgreSQL\15\bin\psql.exe' -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres123';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Password changed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to change password: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to execute psql: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Restore pg_hba.conf
Write-Host ""
Write-Host "Step 5: Restoring pg_hba.conf security settings..." -ForegroundColor Yellow
try {
    Copy-Item -Path $pgHbaBackup -Destination $pgHbaPath -Force
    Write-Host "[OK] Security settings restored" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to restore pg_hba.conf: $_" -ForegroundColor Red
    exit 1
}

# Step 6: Restart PostgreSQL again
Write-Host ""
Write-Host "Step 6: Restarting PostgreSQL with secure settings..." -ForegroundColor Yellow
try {
    Restart-Service postgresql-x64-15
    Start-Sleep -Seconds 3
    Write-Host "[OK] Service restarted" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to restart service: $_" -ForegroundColor Red
    exit 1
}

# Step 7: Test the new password
Write-Host ""
Write-Host "Step 7: Testing new password..." -ForegroundColor Yellow
$env:PGPASSWORD = 'postgres123'
$result = & 'C:\Program Files\PostgreSQL\15\bin\psql.exe' -U postgres -h localhost -p 5432 -d tcu_ceaa_db -c "SELECT current_database();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "PostgreSQL password is now: postgres123" -ForegroundColor Cyan
    Write-Host "Database 'tcu_ceaa_db' is accessible" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now run Django:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Gray
    Write-Host "  python manage.py runserver" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[ERROR] Connection test failed: $result" -ForegroundColor Red
    Write-Host "Please check the error message above" -ForegroundColor Yellow
}

# Cleanup
Remove-Item $pgHbaBackup -ErrorAction SilentlyContinue
