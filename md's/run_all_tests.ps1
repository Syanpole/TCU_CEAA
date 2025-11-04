# TCU CEAA - Complete Test Suite Runner
# Runs both Frontend and Backend tests

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  TCU CEAA - COMPLETE TEST SUITE" -ForegroundColor White
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$frontendPassed = $false
$backendPassed = $false
$frontendTests = 0
$backendTests = 0

# FRONTEND TESTS
Write-Host "FRONTEND TESTS (React + TypeScript + Jest)" -ForegroundColor Yellow
Write-Host "-------------------------------------------------------------" -ForegroundColor Yellow
Write-Host ""

Push-Location frontend

try {
    Write-Host "Running Jest tests..." -ForegroundColor Cyan
    $frontendOutput = npm test -- --watchAll=false --coverage --verbose 2>&1 | Out-String
    
    Write-Host $frontendOutput
    
    if ($frontendOutput -match "Tests:\s+(\d+)\s+passed") {
        $frontendTests = [int]$matches[1]
        $frontendPassed = $true
        Write-Host "[OK] Frontend: $frontendTests tests passed" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Frontend tests failed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "[ERROR] Error running frontend tests: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "-------------------------------------------------------------" -ForegroundColor Gray
Write-Host ""

# BACKEND TESTS
Write-Host "BACKEND TESTS (Django + Python)" -ForegroundColor Magenta
Write-Host "-------------------------------------------------------------" -ForegroundColor Magenta
Write-Host ""

Push-Location backend

try {
    Write-Host "Running Django tests..." -ForegroundColor Cyan
    $backendOutput = python manage.py test --verbosity=2 2>&1 | Out-String
    
    Write-Host $backendOutput
    
    if ($backendOutput -match "Ran (\d+) test") {
        $backendTests = [int]$matches[1]
        
        if ($backendOutput -match "OK") {
            $backendPassed = $true
            Write-Host "[OK] Backend: $backendTests tests passed" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] Backend: Some tests failed" -ForegroundColor Red
        }
    } else {
        Write-Host "[FAIL] Backend tests failed" -ForegroundColor Red
    }
    
} catch {
    Write-Host "[ERROR] Error running backend tests: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# SUMMARY
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  TEST SUMMARY" -ForegroundColor White
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

if ($frontendPassed) {
    Write-Host "[PASS] Frontend Tests: $frontendTests" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Frontend Tests" -ForegroundColor Red
}

Write-Host ""

if ($backendPassed) {
    Write-Host "[PASS] Backend Tests: $backendTests" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Backend Tests" -ForegroundColor Red
}

Write-Host ""
Write-Host "-------------------------------------------------------------" -ForegroundColor Gray

$totalTests = $frontendTests + $backendTests
Write-Host ""
Write-Host "TOTAL TESTS: $totalTests" -ForegroundColor Cyan
Write-Host "  Frontend: $frontendTests" -ForegroundColor White
Write-Host "  Backend:  $backendTests" -ForegroundColor White
Write-Host ""
$durationStr = $duration.TotalSeconds.ToString("F2")
Write-Host "Duration: $durationStr seconds" -ForegroundColor White

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan

if ($frontendPassed -and $backendPassed) {
    Write-Host ""
    Write-Host "*** ALL TESTS PASSED ***" -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host ""
    Write-Host "*** SOME TESTS FAILED ***" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
