# Direct pgAdmin Fix - Force Password Reset
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "pgAdmin Connection Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$pgBinPath = "C:\Program Files\PostgreSQL\17\bin"
$currentPassword = "postgre123"
$newPassword = "admin123"

Write-Host "`nStep 1: Testing current password (postgre123)..." -ForegroundColor Yellow
$env:PGPASSWORD = $currentPassword
$test = & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT 1;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Current password works!`n" -ForegroundColor Green
    
    Write-Host "Step 2: Changing to simple password (admin123)..." -ForegroundColor Yellow
    & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Password changed!`n" -ForegroundColor Green
        
        Write-Host "Step 3: Verifying new password..." -ForegroundColor Yellow
        $env:PGPASSWORD = $newPassword
        $verify = & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d tcu_ceaa_db -c "SELECT current_user, current_database();" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "New password verified!`n" -ForegroundColor Green
            
            # Update .env
            $envPath = "C:\xampp\htdocs\TCU_CEAA\backend\.env"
            $envContent = Get-Content $envPath
            $newEnvContent = $envContent | ForEach-Object {
                if ($_ -match "^DB_PASSWORD=") {
                    "DB_PASSWORD=$newPassword"
                } else {
                    $_
                }
            }
            $newEnvContent | Set-Content -Path $envPath -Force
            Write-Host ".env file updated`n" -ForegroundColor Green
            
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "SUCCESS!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "`nNew Password: $newPassword" -ForegroundColor Yellow
            Write-Host "`nFor pgAdmin:" -ForegroundColor Cyan
            Write-Host "  1. Close pgAdmin completely (File → Exit)" -ForegroundColor White
            Write-Host "  2. Reopen pgAdmin" -ForegroundColor White
            Write-Host "  3. When it asks for password, enter: $newPassword" -ForegroundColor Yellow
            Write-Host "`nOR delete the server and create new with:" -ForegroundColor Cyan
            Write-Host "  Password: $newPassword" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✗ Current password doesn't work`n" -ForegroundColor Red
    Write-Host "Running full reset...`n" -ForegroundColor Yellow
    
    # Try with postgres123 (server password)
    $env:PGPASSWORD = "postgres123"
    & "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Password reset to: $newPassword" -ForegroundColor Green
        
        # Update .env
        $envPath = "C:\xampp\htdocs\TCU_CEAA\backend\.env"
        $envContent = Get-Content $envPath
        $newEnvContent = $envContent | ForEach-Object {
            if ($_ -match "^DB_PASSWORD=") {
                "DB_PASSWORD=$newPassword"
            } else {
                $_
            }
        }
        $newEnvContent | Set-Content -Path $envPath -Force
        Write-Host ".env updated" -ForegroundColor Green
    }
}

$env:PGPASSWORD = $null
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
