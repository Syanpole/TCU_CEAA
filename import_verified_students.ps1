# Import Verified Students from CSV
# This script imports students from backend/BSCS_4th_Year_List-1.csv into the database

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TCU-CEAA: Import Verified Students from CSV" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$csvFile = ".\backend\BSCS_4th_Year_List-1.csv"
$importScript = ".\backend\import_students_from_csv.py"

# Check if CSV file exists
if (-Not (Test-Path $csvFile)) {
    Write-Host "❌ Error: CSV file not found at: $csvFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please make sure BSCS_4th_Year_List-1.csv is in the backend directory." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Found CSV file: $csvFile" -ForegroundColor Green
Write-Host "✅ Found import script: $importScript" -ForegroundColor Green
Write-Host ""

# Count students in CSV
$studentCount = (Get-Content $csvFile | Measure-Object -Line).Lines - 1
Write-Host "📋 CSV contains $studentCount students" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔄 Importing students into database..." -ForegroundColor Cyan
Write-Host ""

# Run the import script
try {
    python $importScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "  ✅ Import Complete!" -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "HOW TO USE:" -ForegroundColor Yellow
        Write-Host "1. Edit backend\BSCS_4th_Year_List-1.csv to add/update students" -ForegroundColor White
        Write-Host "2. Run this script again: .\import_verified_students.ps1" -ForegroundColor White
        Write-Host "3. Changes will be automatically synced to the database" -ForegroundColor White
        Write-Host ""
        Write-Host "Students can now register using their Student Number!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Import failed. Please check the error messages above." -ForegroundColor Red
        Write-Host ""
    }
} catch {
    Write-Host "❌ Error running import script: $_" -ForegroundColor Red
    exit 1
}
