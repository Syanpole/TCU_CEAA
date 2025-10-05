# ============================================================================
# RESTORE ALL BACKED UP FILES
# ============================================================================
# This script restores ALL files from the backup to their original locations
# WARNING: This will overwrite current files with the backup versions!
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║          RESTORE BACKUP - October 6, 2025                   ║" -ForegroundColor Yellow
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

Write-Host "⚠️  WARNING: This will restore ALL backup files and OVERWRITE current versions!" -ForegroundColor Red
Write-Host ""
$confirmation = Read-Host "Are you sure you want to continue? (yes/no)"

if ($confirmation -ne "yes") {
    Write-Host "`n❌ Restore cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🔄 Starting restore process...`n" -ForegroundColor Cyan

$backupDir = $PSScriptRoot
$projectRoot = Split-Path $backupDir -Parent
$filesRestored = 0
$errors = 0

# Get all files in backup (excluding this script and README)
Get-ChildItem -Path $backupDir -Recurse -File | Where-Object { 
    $_.Name -notlike "*.ps1" -and $_.Name -notlike "README*.md" 
} | ForEach-Object {
    try {
        # Calculate relative path from backup directory
        $relativePath = $_.FullName.Replace($backupDir + "\", "")
        $destination = Join-Path $projectRoot $relativePath
        
        # Ensure destination directory exists
        $destDir = Split-Path $destination -Parent
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        # Copy file
        Copy-Item -Path $_.FullName -Destination $destination -Force
        Write-Host "✅ Restored: $relativePath" -ForegroundColor Green
        $filesRestored++
    }
    catch {
        Write-Host "❌ Error restoring $relativePath : $_" -ForegroundColor Red
        $errors++
    }
}

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    RESTORE COMPLETE                         ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "📊 Statistics:" -ForegroundColor White
Write-Host "   Files Restored: $filesRestored" -ForegroundColor Green
Write-Host "   Errors: $errors" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Red" })

if ($filesRestored -gt 0) {
    Write-Host "`n✅ Backup restoration completed successfully!" -ForegroundColor Green
    Write-Host "`n🔍 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Test your application" -ForegroundColor White
    Write-Host "   2. Run: .\run_all_tests.ps1" -ForegroundColor White
    Write-Host "   3. Verify all features work correctly" -ForegroundColor White
} else {
    Write-Host "`n⚠️  No files were restored. Check the backup directory." -ForegroundColor Yellow
}

Write-Host ""
