# Check and Setup PostgreSQL 17 Database
# This script checks if the database exists and creates it if needed

$env:PGPASSWORD = "postgre123"

Write-Host "Checking if database 'tcu_ceaa_db' exists on PostgreSQL 17..." -ForegroundColor Cyan

# Check if database exists
$dbExists = & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -lqt | Select-String -Pattern "tcu_ceaa_db"

if ($dbExists) {
    Write-Host "✓ Database 'tcu_ceaa_db' already exists!" -ForegroundColor Green
} else {
    Write-Host "Database 'tcu_ceaa_db' not found. Creating it..." -ForegroundColor Yellow
    & "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -c "CREATE DATABASE tcu_ceaa_db;"
    Write-Host "✓ Database 'tcu_ceaa_db' created successfully!" -ForegroundColor Green
}

Write-Host "`nYou can now run Django migrations with:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python manage.py migrate" -ForegroundColor White

Remove-Item Env:\PGPASSWORD
