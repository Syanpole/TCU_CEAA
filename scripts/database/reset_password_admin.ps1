# Complete PostgreSQL Password Reset with Admin Privileges
# This script will properly reset the PostgreSQL password

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Password Reset (Admin Mode)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Not running as Administrator!" -ForegroundColor Yellow
    Write-Host "Attempting to restart with admin privileges..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green

$pgVersion = "17"
$pgBinPath = "C:\Program Files\PostgreSQL\$pgVersion\bin"
$pgDataPath = "C:\Program Files\PostgreSQL\$pgVersion\data"
$pgHbaConf = "$pgDataPath\pg_hba.conf"
$serviceName = "postgresql-x64-$pgVersion"

# Step 1: Stop PostgreSQL
Write-Host "`nStep 1: Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service -Name $serviceName -Force
Start-Sleep -Seconds 3
Write-Host "✓ PostgreSQL stopped" -ForegroundColor Green

# Step 2: Backup and modify pg_hba.conf to use 'trust' authentication
Write-Host "`nStep 2: Modifying pg_hba.conf..." -ForegroundColor Yellow
$backupPath = "$pgHbaConf.backup_trust_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $pgHbaConf -Destination $backupPath -Force
Write-Host "✓ Backup created: $backupPath" -ForegroundColor Green

# Read and modify pg_hba.conf
$hbaContent = Get-Content $pgHbaConf
$newContent = @()
$inHostSection = $false

foreach ($line in $hbaContent) {
    if ($line -match "^# IPv4 local connections:") {
        $newContent += $line
        $inHostSection = $true
    }
    elseif ($line -match "^# IPv6 local connections:") {
        $newContent += $line
        $inHostSection = $true
    }
    elseif ($line -match "^host\s+" -and -not ($line -match "^#")) {
        # Replace all host entries with trust temporarily
        $parts = $line -split '\s+'
        if ($parts.Count -ge 5) {
            $newLine = "host    all             all             " + $parts[3] + "            trust"
            $newContent += $newLine
            Write-Host "  Modified: $line" -ForegroundColor Gray
            Write-Host "       To: $newLine" -ForegroundColor Gray
        } else {
            $newContent += $line
        }
    }
    else {
        $newContent += $line
    }
}

$newContent | Set-Content -Path $pgHbaConf -Force
Write-Host "✓ pg_hba.conf set to trust authentication" -ForegroundColor Green

# Step 3: Start PostgreSQL
Write-Host "`nStep 3: Starting PostgreSQL service..." -ForegroundColor Yellow
Start-Service -Name $serviceName
Start-Sleep -Seconds 5
Write-Host "✓ PostgreSQL started" -ForegroundColor Green

# Step 4: Change password without authentication
Write-Host "`nStep 4: Setting new password..." -ForegroundColor Yellow
$newPassword = "postgre123"

$env:PGPASSWORD = $null
$result = & "$pgBinPath\psql.exe" -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Password successfully set to: $newPassword" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to set password" -ForegroundColor Red
    Write-Host "Error: $result" -ForegroundColor Red
}

# Step 5: Restore pg_hba.conf to use md5 authentication
Write-Host "`nStep 5: Restoring md5 authentication..." -ForegroundColor Yellow

$finalContent = Get-Content $pgHbaConf | ForEach-Object {
    if ($_ -match "^host\s+.*\s+trust$") {
        $_ -replace "trust$", "scram-sha-256"
    } else {
        $_
    }
}

$finalContent | Set-Content -Path $pgHbaConf -Force
Write-Host "✓ pg_hba.conf restored to scram-sha-256 authentication" -ForegroundColor Green

# Step 6: Restart PostgreSQL
Write-Host "`nStep 6: Restarting PostgreSQL..." -ForegroundColor Yellow
Restart-Service -Name $serviceName -Force
Start-Sleep -Seconds 5
Write-Host "✓ PostgreSQL restarted" -ForegroundColor Green

# Step 7: Test connection
Write-Host "`nStep 7: Testing connection..." -ForegroundColor Yellow
$env:PGPASSWORD = $newPassword

$testResult = & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT 'SUCCESS!' as connection_test;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✓ SUCCESS! Password Reset Complete" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nPostgreSQL Connection Details:" -ForegroundColor Cyan
    Write-Host "  Host: 127.0.0.1" -ForegroundColor White
    Write-Host "  Port: 5432" -ForegroundColor White
    Write-Host "  Username: postgres" -ForegroundColor White
    Write-Host "  Password: $newPassword" -ForegroundColor White
    Write-Host "`nYou can now use this password in pgAdmin!" -ForegroundColor Green
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "✗ Connection Test Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Red
    
    Write-Host "`nTrying with scram-sha-256..." -ForegroundColor Yellow
    # Show pg_hba.conf content
    Write-Host "`nCurrent pg_hba.conf host entries:" -ForegroundColor Cyan
    Get-Content $pgHbaConf | Select-String "^host" | ForEach-Object { Write-Host "  $_" }
}

$env:PGPASSWORD = $null

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
