# Complete PostgreSQL Password Fix Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Password Reset & Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# PostgreSQL 17 paths
$pgVersion = "17"
$pgBinPath = "C:\Program Files\PostgreSQL\$pgVersion\bin"
$pgDataPath = "C:\Program Files\PostgreSQL\$pgVersion\data"
$pgHbaConf = "$pgDataPath\pg_hba.conf"

# Check if PostgreSQL is running
Write-Host "`nStep 1: Checking PostgreSQL service..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql-x64-$pgVersion" -ErrorAction SilentlyContinue

if ($pgService.Status -ne "Running") {
    Write-Host "PostgreSQL $pgVersion is not running. Starting service..." -ForegroundColor Red
    Start-Service -Name "postgresql-x64-$pgVersion"
    Start-Sleep -Seconds 3
} else {
    Write-Host "PostgreSQL $pgVersion is running." -ForegroundColor Green
}

# Step 2: Modify pg_hba.conf to allow password authentication
Write-Host "`nStep 2: Configuring pg_hba.conf for password authentication..." -ForegroundColor Yellow

# Backup pg_hba.conf
$backupPath = "$pgHbaConf.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item -Path $pgHbaConf -Destination $backupPath -Force
Write-Host "Backup created: $backupPath" -ForegroundColor Green

# Read current pg_hba.conf
$hbaContent = Get-Content $pgHbaConf

# Modify authentication methods to 'md5' for local connections
$newHbaContent = $hbaContent | ForEach-Object {
    if ($_ -match "^host\s+all\s+all\s+127\.0\.0\.1/32\s+" -and $_ -notmatch "#") {
        "host    all             all             127.0.0.1/32            md5"
    }
    elseif ($_ -match "^host\s+all\s+all\s+::1/128\s+" -and $_ -notmatch "#") {
        "host    all             all             ::1/128                 md5"
    }
    elseif ($_ -match "^host\s+all\s+all\s+0\.0\.0\.0/0\s+" -and $_ -notmatch "#") {
        "host    all             all             0.0.0.0/0               md5"
    }
    else {
        $_
    }
}

# Save modified pg_hba.conf
$newHbaContent | Set-Content -Path $pgHbaConf -Force
Write-Host "pg_hba.conf updated to use md5 authentication" -ForegroundColor Green

# Step 3: Reload PostgreSQL configuration
Write-Host "`nStep 3: Reloading PostgreSQL configuration..." -ForegroundColor Yellow
& "$pgBinPath\pg_ctl.exe" reload -D "$pgDataPath"
Start-Sleep -Seconds 2

# Step 4: Reset password using different authentication methods
Write-Host "`nStep 4: Attempting to reset password..." -ForegroundColor Yellow

$passwords = @("postgres123", "postgre123", "postgres", "admin")
$newPassword = "postgre123"
$connected = $false

foreach ($pwd in $passwords) {
    try {
        Write-Host "Trying with password: $pwd" -ForegroundColor Gray
        $env:PGPASSWORD = $pwd
        
        # Try to connect and change password
        $result = & "$pgBinPath\psql.exe" -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully connected with password: $pwd" -ForegroundColor Green
            Write-Host "✓ Password changed to: $newPassword" -ForegroundColor Green
            $connected = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $connected) {
    Write-Host "✗ Could not connect with any common password." -ForegroundColor Red
    Write-Host "`nTrying Windows authentication (trust method)..." -ForegroundColor Yellow
    
    # Temporarily change pg_hba.conf to trust
    $trustContent = Get-Content $pgHbaConf | ForEach-Object {
        if ($_ -match "^host\s+all\s+all\s+127\.0\.0\.1/32\s+md5") {
            "host    all             all             127.0.0.1/32            trust"
        } else { $_ }
    }
    $trustContent | Set-Content -Path $pgHbaConf -Force
    
    # Reload
    & "$pgBinPath\pg_ctl.exe" reload -D "$pgDataPath"
    Start-Sleep -Seconds 2
    
    # Try without password
    $env:PGPASSWORD = $null
    & "$pgBinPath\psql.exe" -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';"
    
    # Restore md5 authentication
    $newHbaContent | Set-Content -Path $pgHbaConf -Force
    & "$pgBinPath\pg_ctl.exe" reload -D "$pgDataPath"
    Start-Sleep -Seconds 2
}

# Step 5: Test new connection
Write-Host "`nStep 5: Testing connection with new password..." -ForegroundColor Yellow
$env:PGPASSWORD = $newPassword

$testResult = & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT 'Connection successful!' as status;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "PostgreSQL Password: $newPassword" -ForegroundColor Green
    Write-Host "Host: 127.0.0.1" -ForegroundColor Green
    Write-Host "Port: 5432" -ForegroundColor Green
    Write-Host "User: postgres" -ForegroundColor Green
    Write-Host "`nYou can now connect to PostgreSQL using:" -ForegroundColor Cyan
    Write-Host "- pgAdmin with password: $newPassword" -ForegroundColor Cyan
    Write-Host "- Django (already configured in .env)" -ForegroundColor Cyan
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "FAILED" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Could not establish connection." -ForegroundColor Red
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
    Write-Host "`nPlease check:" -ForegroundColor Yellow
    Write-Host "1. PostgreSQL service is running" -ForegroundColor Yellow
    Write-Host "2. Port 5432 is not blocked" -ForegroundColor Yellow
    Write-Host "3. pg_hba.conf is properly configured" -ForegroundColor Yellow
}

# Cleanup
$env:PGPASSWORD = $null
