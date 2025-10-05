# Quick Backend Test Runner
# Usage: .\test_backend.ps1

Write-Host "`n🧪 Running Backend Unit Tests...`n" -ForegroundColor Cyan

cd backend
$env:PYTHONIOENCODING = 'utf-8'
python manage.py test myapp.tests --verbosity=2

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ All backend tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Some backend tests failed!" -ForegroundColor Red
}
