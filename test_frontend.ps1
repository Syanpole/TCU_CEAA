# Quick Frontend Test Runner
# Usage: .\test_frontend.ps1

Write-Host "`n🎨 Running Frontend Unit Tests...`n" -ForegroundColor Cyan

cd frontend
npm test -- --watchAll=false --passWithNoTests

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All frontend tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some frontend tests failed!" -ForegroundColor Red
}
