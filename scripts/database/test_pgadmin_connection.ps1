# Test PostgreSQL Connection - All possible scenarios
Write-Host "Testing PostgreSQL Connection..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$pgBinPath = "C:\Program Files\PostgreSQL\17\bin"
$password = "postgre123"

Write-Host "`nTest 1: Connection to localhost" -ForegroundColor Yellow
$env:PGPASSWORD = $password
& "$pgBinPath\psql.exe" -U postgres -h localhost -p 5432 -d postgres -c "SELECT current_user, current_database();"
Write-Host "Result: Exit Code = $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })

Write-Host "`nTest 2: Connection to 127.0.0.1" -ForegroundColor Yellow
$env:PGPASSWORD = $password
& "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT current_user, current_database();"
Write-Host "Result: Exit Code = $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })

Write-Host "`nTest 3: Check if database 'tcu_ceaa_db' exists" -ForegroundColor Yellow
$env:PGPASSWORD = $password
& "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT datname FROM pg_database WHERE datname = 'tcu_ceaa_db';"
Write-Host "Result: Exit Code = $LASTEXITCODE" -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })

Write-Host "`nTest 4: List all databases" -ForegroundColor Yellow
$env:PGPASSWORD = $password
& "$pgBinPath\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "\l"

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "pgAdmin Connection Details:" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Host: 127.0.0.1 (or localhost)" -ForegroundColor White
Write-Host "Port: 5432" -ForegroundColor White
Write-Host "Database: postgres (or tcu_ceaa_db)" -ForegroundColor White
Write-Host "Username: postgres" -ForegroundColor White
Write-Host "Password: postgre123" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan

$env:PGPASSWORD = $null
