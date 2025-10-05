# ============================================================================
# TCU-CEAA Comprehensive Test Runner
# ============================================================================
# This script runs all unit tests for both backend and frontend
# Usage: .\run_all_tests.ps1
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TCU-CEAA COMPREHENSIVE UNIT TEST SUITE                  ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$startTime = Get-Date
$backendPassed = $false
$frontendPassed = $false

# ============================================================================
# BACKEND TESTS (Django/Python)
# ============================================================================

Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│  RUNNING BACKEND TESTS (Django/Python)                      │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Yellow

Push-Location backend

try {
    # Set UTF-8 encoding to handle emoji characters
    $env:PYTHONIOENCODING = 'utf-8'
    
    Write-Host "Running Django unit tests..." -ForegroundColor White
    python manage.py test myapp.tests --verbosity=2
    
    if ($LASTEXITCODE -eq 0) {
        $backendPassed = $true
        Write-Host "`n[OK] BACKEND TESTS PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n[FAILED] BACKEND TESTS FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "`n[ERROR] RUNNING BACKEND TESTS: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# ============================================================================
# FRONTEND TESTS (React/TypeScript)
# ============================================================================

Write-Host "`n┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Yellow
Write-Host "│  RUNNING FRONTEND TESTS (React/TypeScript)                  │" -ForegroundColor Yellow
Write-Host "└─────────────────────────────────────────────────────────────┘`n" -ForegroundColor Yellow

Push-Location frontend

try {
    Write-Host "Running React unit tests..." -ForegroundColor White
    npm test -- --watchAll=false --passWithNoTests
    
    if ($LASTEXITCODE -eq 0) {
        $frontendPassed = $true
        Write-Host "`n[OK] FRONTEND TESTS PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n[FAILED] FRONTEND TESTS FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "`n[ERROR] RUNNING FRONTEND TESTS: $_" -ForegroundColor Red
} finally {
    Pop-Location
}

# ============================================================================
# FINAL SUMMARY
# ============================================================================

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                     TEST SUMMARY                            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Backend Tests:  " -NoNewline
if ($backendPassed) {
    Write-Host "[OK] PASSED" -ForegroundColor Green
} else {
    Write-Host "[FAILED] FAILED" -ForegroundColor Red
}

Write-Host "Frontend Tests: " -NoNewline
if ($frontendPassed) {
    Write-Host "[OK] PASSED" -ForegroundColor Green
} else {
    Write-Host "[FAILED] FAILED" -ForegroundColor Red
}

$durationSeconds = [math]::Round($duration.TotalSeconds, 2)
Write-Host "`nTotal Duration: $durationSeconds seconds" -ForegroundColor Cyan

if ($backendPassed -and $frontendPassed) {
    Write-Host "`n[SUCCESS] ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n[WARNING] SOME TESTS FAILED" -ForegroundColor Red
    exit 1
}
