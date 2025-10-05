# Frontend Test with Coverage Report
# Usage: .\test_frontend_coverage.ps1

Write-Host "`n📊 Running Frontend Tests with Coverage...`n" -ForegroundColor Cyan

cd frontend
npm test -- --watchAll=false --coverage --passWithNoTests

Write-Host "`n✅ Coverage report generated!" -ForegroundColor Green
Write-Host "📁 View detailed coverage at: frontend/coverage/lcov-report/index.html" -ForegroundColor Yellow
