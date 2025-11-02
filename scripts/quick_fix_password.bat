@echo off
echo ================================================
echo PostgreSQL Password Quick Fix
echo ================================================
echo.
echo This script will:
echo 1. Try common passwords
echo 2. Reset password to 'postgre123' if needed
echo.
echo Please run as ADMINISTRATOR
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0fix_postgresql_password.ps1"

echo.
echo Done! Press any key to exit...
pause
