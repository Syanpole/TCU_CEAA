# Mobile Testing Setup Script for TCU_CEAA
# This script sets up the development environment for mobile device testing

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   TCU CEAA - Mobile Testing Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Get local IP address
Write-Host "Finding your computer's IP address..." -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress

if (-not $ipAddress) {
    Write-Host "ERROR: Could not find local IP address. Make sure you're connected to WiFi." -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual check: Run 'ipconfig' and look for IPv4 Address" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "SUCCESS: Found IP Address: $ipAddress" -ForegroundColor Green
Write-Host ""

# Update backend ALLOWED_HOSTS
Write-Host "Updating backend ALLOWED_HOSTS..." -ForegroundColor Yellow
$settingsPath = "backend\backend_project\settings.py"

if (Test-Path $settingsPath) {
    $settingsContent = Get-Content $settingsPath -Raw
    
    # Check if ALLOWED_HOSTS already includes the IP
    if ($settingsContent -notmatch [regex]::Escape($ipAddress)) {
        # Backup original settings
        Copy-Item $settingsPath "$settingsPath.backup" -Force
        Write-Host "   Backup created: $settingsPath.backup" -ForegroundColor Gray
        
        # Update ALLOWED_HOSTS
        $settingsContent = $settingsContent -replace "ALLOWED_HOSTS = \[(.*?)\]", "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '$ipAddress', '*']"
        Set-Content $settingsPath $settingsContent
        Write-Host "SUCCESS: ALLOWED_HOSTS updated with $ipAddress" -ForegroundColor Green
    } else {
        Write-Host "SUCCESS: ALLOWED_HOSTS already includes $ipAddress" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: Could not find settings.py at $settingsPath" -ForegroundColor Yellow
}
Write-Host ""

# Display connection information
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Mobile Testing URLs" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL:" -ForegroundColor Green
Write-Host "   http://${ipAddress}:3002" -ForegroundColor White
Write-Host ""
Write-Host "Backend URL:" -ForegroundColor Green
Write-Host "   http://${ipAddress}:8000" -ForegroundColor White
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Ask user what to start
Write-Host "What would you like to start?" -ForegroundColor Yellow
Write-Host "  1. Frontend only (React)" -ForegroundColor White
Write-Host "  2. Backend only (Django)" -ForegroundColor White
Write-Host "  3. Both Frontend and Backend" -ForegroundColor White
Write-Host "  4. Just show URLs (don't start anything)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Frontend on network..." -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: On your phone, make sure to:" -ForegroundColor Yellow
        Write-Host "   1. Connect to the SAME WiFi as this computer" -ForegroundColor White
        Write-Host "   2. Open browser and go to: http://${ipAddress}:3002" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Ctrl+C to stop the server when done testing" -ForegroundColor Gray
        Write-Host ""
        Start-Sleep -Seconds 3
        
        Set-Location frontend
        $env:HOST = "0.0.0.0"
        npm start
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Backend on network..." -ForegroundColor Green
        Write-Host ""
        Write-Host "Backend will be accessible at: http://${ipAddress}:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Ctrl+C to stop the server when done testing" -ForegroundColor Gray
        Write-Host ""
        Start-Sleep -Seconds 3
        
        Set-Location backend
        python manage.py runserver 0.0.0.0:8000
    }
    "3" {
        Write-Host ""
        Write-Host "Starting Both Frontend and Backend..." -ForegroundColor Green
        Write-Host ""
        Write-Host "This will open 2 terminal windows:" -ForegroundColor Yellow
        Write-Host "   - Frontend: http://${ipAddress}:3002" -ForegroundColor White
        Write-Host "   - Backend: http://${ipAddress}:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "On your phone:" -ForegroundColor Cyan
        Write-Host "   1. Connect to SAME WiFi" -ForegroundColor White
        Write-Host "   2. Open: http://${ipAddress}:3002" -ForegroundColor White
        Write-Host ""
        Start-Sleep -Seconds 3
        
        # Start backend in new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python manage.py runserver 0.0.0.0:8000"
        
        Start-Sleep -Seconds 2
        
        # Start frontend in new window
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; `$env:HOST='0.0.0.0'; npm start"
        
        Write-Host ""
        Write-Host "SUCCESS: Servers starting in separate windows!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Use this URL on your phone: http://${ipAddress}:3002" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press any key to close this window..." -ForegroundColor Gray
        Read-Host
    }
    "4" {
        Write-Host ""
        Write-Host "Connection Information:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your IP: $ipAddress" -ForegroundColor White
        Write-Host "Frontend: http://${ipAddress}:3002" -ForegroundColor White
        Write-Host "Backend: http://${ipAddress}:8000" -ForegroundColor White
        Write-Host ""
        Write-Host "Manual Start Commands:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Frontend:" -ForegroundColor Green
        Write-Host "   cd frontend" -ForegroundColor White
        Write-Host "   `$env:HOST='0.0.0.0'" -ForegroundColor White
        Write-Host "   npm start" -ForegroundColor White
        Write-Host ""
        Write-Host "Backend:" -ForegroundColor Green
        Write-Host "   cd backend" -ForegroundColor White
        Write-Host "   python manage.py runserver 0.0.0.0:8000" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
    default {
        Write-Host ""
        Write-Host "ERROR: Invalid choice. Exiting..." -ForegroundColor Red
        Start-Sleep -Seconds 2
    }
}
