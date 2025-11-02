# Start PostgreSQL 17 Service
# Run this script as Administrator

Write-Host "Stopping PostgreSQL 15..." -ForegroundColor Yellow
Stop-Service -Name postgresql-x64-15 -Force -ErrorAction SilentlyContinue

Write-Host "Starting PostgreSQL 17..." -ForegroundColor Green
Start-Service -Name postgresql-x64-17

Write-Host "Checking service status..." -ForegroundColor Cyan
Get-Service -Name postgresql-x64-17

Write-Host "`n✓ PostgreSQL 17 is now running!" -ForegroundColor Green
Write-Host "You can now run Django with: python manage.py runserver" -ForegroundColor Cyan
