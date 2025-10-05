@echo off
echo ========================================
echo PostgreSQL 17 Service Starter
echo ========================================
echo.
echo This will:
echo 1. Stop PostgreSQL 15
echo 2. Start PostgreSQL 17
echo.
echo Please confirm you are running as Administrator...
pause

net stop postgresql-x64-15
net start postgresql-x64-17

echo.
echo ========================================
echo Checking service status...
echo ========================================
powershell -Command "Get-Service -Name postgresql-x64-17"

echo.
echo ========================================
echo PostgreSQL 17 should now be running!
echo ========================================
pause
