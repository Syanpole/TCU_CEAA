# Grade Eligibility Fix - FINAL OFFICIAL VERSION
# TCU-CEAA Grading Criteria Implementation

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TCU-CEAA GRADE ELIGIBILITY FIX" -ForegroundColor Cyan
Write-Host "  OFFICIAL CRITERIA IMPLEMENTATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OFFICIAL ELIGIBILITY CRITERIA:" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow
Write-Host "GWA 1.0 to 1.75  → Basic (P5,000) + Merit (P5,000) = P10,000" -ForegroundColor Green
Write-Host "GWA 1.76 to 2.5  → Basic (P5,000) ONLY" -ForegroundColor Yellow
Write-Host "GWA 2.51 and above → NOT ELIGIBLE" -ForegroundColor Red
Write-Host ""
Write-Host "Additional Requirements:" -ForegroundColor Cyan
Write-Host "  • Total Units >= 15" -ForegroundColor White
Write-Host "  • No Failing Grades" -ForegroundColor White
Write-Host "  • No Incomplete Grades" -ForegroundColor White
Write-Host "  • No Dropped Subjects" -ForegroundColor White
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
        python manage.py fix_grade_eligibility_final --dry-run
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  DRY RUN COMPLETE!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "No changes were saved. Review the output above." -ForegroundColor Yellow
        Write-Host "Run this script again and choose option 2 to apply changes." -ForegroundColor Yellow
    }
    
    "2" {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "  WARNING: DATABASE MODIFICATION" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "This will update all grade submissions in the database." -ForegroundColor Yellow
        Write-Host "Make sure you have reviewed the changes using DRY RUN first." -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "Are you sure you want to proceed? Type 'YES' to confirm"
        
        if ($confirm -eq "YES") {
            Write-Host ""
            Write-Host "Applying fix to all grade submissions..." -ForegroundColor Green
            Write-Host ""
            
            Set-Location backend
            python manage.py fix_grade_eligibility_final
            
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  FIX APPLIED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Refresh your student dashboard" -ForegroundColor White
            Write-Host "  2. Check grade eligibility status" -ForegroundColor White
            Write-Host "  3. Verify allowance amounts are correct" -ForegroundColor White
            Write-Host "  4. Students can now apply for allowances!" -ForegroundColor White
            Write-Host ""
            Write-Host "Grading Criteria Applied:" -ForegroundColor Cyan
            Write-Host "  • GWA 1.0-1.75 = P10,000 (Basic + Merit)" -ForegroundColor Green
            Write-Host "  • GWA 1.76-2.5 = P5,000 (Basic only)" -ForegroundColor Yellow
            Write-Host "  • GWA 2.51+ = P0 (Not eligible)" -ForegroundColor Red
        } else {
            Write-Host ""
            Write-Host "Operation cancelled. No changes were made." -ForegroundColor Yellow
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Exiting without making any changes..." -ForegroundColor Yellow
        Write-Host ""
        exit
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again and enter 1, 2, or 3." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
