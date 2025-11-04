# Grade Eligibility Fix - Quick Run Script
# This script will fix the grading eligibility for all students

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GRADE ELIGIBILITY FIX TOOL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will fix the grading eligibility criteria:" -ForegroundColor Yellow
Write-Host "  - Basic Allowance: GWA >= 80% (2.25 or better)" -ForegroundColor White
Write-Host "  - Merit Incentive: GWA >= 84.5% (2.0 or better)" -ForegroundColor White
Write-Host ""

# Ask user what they want to do
Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host "  1. DRY RUN (preview changes without saving)" -ForegroundColor White
Write-Host "  2. APPLY FIX (update all grade submissions)" -ForegroundColor White
Write-Host "  3. EXIT" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1, 2, or 3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running DRY RUN..." -ForegroundColor Yellow
        Write-Host "This will show what changes would be made WITHOUT saving them." -ForegroundColor Yellow
        Write-Host ""
        
        Set-Location backend
        python manage.py fix_grade_eligibility --dry-run
        
        Write-Host ""
        Write-Host "DRY RUN COMPLETE!" -ForegroundColor Green
        Write-Host "No changes were saved. Review the output above." -ForegroundColor Yellow
        Write-Host "Run this script again and choose option 2 to apply changes." -ForegroundColor Yellow
    }
    
    "2" {
        Write-Host ""
        Write-Host "APPLYING FIX..." -ForegroundColor Yellow
        Write-Host "This will update all grade submissions in the database." -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "Are you sure you want to proceed? (yes/no)"
        
        if ($confirm -eq "yes") {
            Set-Location backend
            python manage.py fix_grade_eligibility
            
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  FIX APPLIED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Refresh your student dashboard" -ForegroundColor White
            Write-Host "  2. Check grade eligibility" -ForegroundColor White
            Write-Host "  3. Students can now apply for allowances!" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "Fix cancelled." -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
