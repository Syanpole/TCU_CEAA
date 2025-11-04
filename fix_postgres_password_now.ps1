# Fix PostgreSQL Password - Set to postgres123
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Password Reset Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check which PostgreSQL is on port 5432
Write-Host "Checking PostgreSQL services..." -ForegroundColor Yellow
Get-Service -Name postgresql* | Where-Object {$_.Status -eq 'Running'} | Format-Table Name, Status

# Try common passwords
$passwords = @('postgres123', 'admin123', 'postgres', 'admin', '123456', 'password')

foreach ($pwd in $passwords) {
    Write-Host "Trying password: $pwd" -ForegroundColor Gray
    $env:PGPASSWORD = $pwd
    
    $result = & 'C:\Program Files\PostgreSQL\15\bin\psql.exe' -U postgres -h localhost -p 5432 -d postgres -c "SELECT 'SUCCESS' as result;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Current password found: $pwd" -ForegroundColor Green
        Write-Host ""
        Write-Host "Now setting password to 'postgres123'..." -ForegroundColor Yellow
        
        & 'C:\Program Files\PostgreSQL\15\bin\psql.exe' -U postgres -h localhost -p 5432 -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres123';"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Password successfully changed to 'postgres123'" -ForegroundColor Green
            Write-Host ""
            Write-Host "Testing new password..." -ForegroundColor Yellow
            $env:PGPASSWORD = 'postgres123'
            & 'C:\Program Files\PostgreSQL\15\bin\psql.exe' -U postgres -h localhost -p 5432 -d tcu_ceaa_db -c "SELECT current_database();"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "  SUCCESS! Password is now: postgres123" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Your Django server should now work!" -ForegroundColor Cyan
                Write-Host "Run: cd backend; python manage.py runserver" -ForegroundColor Gray
            }
        }
        exit 0
    }
}

Write-Host ""
Write-Host "❌ None of the common passwords worked!" -ForegroundColor Red
Write-Host ""
Write-Host "SOLUTION: We need to reset the password manually" -ForegroundColor Yellow
Write-Host ""
Write-Host "Method 1: Use pgAdmin" -ForegroundColor Cyan
Write-Host "  1. Open pgAdmin 4" -ForegroundColor White
Write-Host "  2. Right-click 'TCU_CEAA_DB' server → Properties" -ForegroundColor White
Write-Host "  3. Go to Connection tab and check the password" -ForegroundColor White
Write-Host "  4. Then update backend\.env file with that password" -ForegroundColor White
Write-Host ""
Write-Host "Method 2: Reset via pg_hba.conf (Advanced)" -ForegroundColor Cyan
Write-Host "  1. Stop PostgreSQL service" -ForegroundColor White
Write-Host "  2. Edit C:\Program Files\PostgreSQL\15\data\pg_hba.conf" -ForegroundColor White
Write-Host "  3. Change 'md5' to 'trust' temporarily" -ForegroundColor White
Write-Host "  4. Restart PostgreSQL" -ForegroundColor White
Write-Host "  5. Run: psql -U postgres -c 'ALTER USER postgres PASSWORD ''postgres123'';'" -ForegroundColor White
Write-Host "  6. Change 'trust' back to 'md5' in pg_hba.conf" -ForegroundColor White
Write-Host "  7. Restart PostgreSQL again" -ForegroundColor White
Write-Host ""
