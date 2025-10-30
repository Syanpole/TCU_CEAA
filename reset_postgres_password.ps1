# Reset PostgreSQL password for postgres user
Write-Host "Resetting PostgreSQL password..." -ForegroundColor Cyan

# Set the PostgreSQL bin path
$pgBinPath = "C:\Program Files\PostgreSQL\17\bin"
$env:PGPASSWORD = "postgres123"  # Current server password

# Reset the password to admin123
Write-Host "Setting new password to 'admin123'..." -ForegroundColor Yellow

& "$pgBinPath\psql.exe" -U postgres -c "ALTER USER postgres WITH PASSWORD 'admin123';"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nPassword successfully changed to: admin123" -ForegroundColor Green
    Write-Host "This matches your .env file configuration." -ForegroundColor Green
} else {
    Write-Host "`nFailed to change password. Trying alternative method..." -ForegroundColor Red
    
    # Try without password prompt (trust authentication)
    $env:PGPASSWORD = $null
    & "$pgBinPath\psql.exe" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD 'admin123';"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nPassword successfully changed to: admin123" -ForegroundColor Green
    }
}

Write-Host "`n=== Testing new connection ===" -ForegroundColor Cyan
$env:PGPASSWORD = "admin123"
& "$pgBinPath\psql.exe" -U postgres -h localhost -c "SELECT version();"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nConnection test successful!" -ForegroundColor Green
} else {
    Write-Host "`nConnection test failed." -ForegroundColor Red
}
