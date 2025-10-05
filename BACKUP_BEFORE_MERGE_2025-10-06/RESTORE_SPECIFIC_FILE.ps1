# ============================================================================
# RESTORE SPECIFIC FILE FROM BACKUP
# ============================================================================
# This script allows you to restore individual files from the backup
# Usage: .\RESTORE_SPECIFIC_FILE.ps1
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          RESTORE SPECIFIC FILE - October 6, 2025           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$backupDir = $PSScriptRoot
$projectRoot = Split-Path $backupDir -Parent

# Get all backed up files (excluding scripts and README)
$allFiles = Get-ChildItem -Path $backupDir -Recurse -File | Where-Object { 
    $_.Name -notlike "*.ps1" -and $_.Name -notlike "README*.md" 
}

if ($allFiles.Count -eq 0) {
    Write-Host "❌ No backup files found!" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Available Files to Restore:`n" -ForegroundColor Yellow

$index = 1
$fileList = @{}

foreach ($file in $allFiles) {
    $relativePath = $file.FullName.Replace($backupDir + "\", "")
    $fileList[$index] = @{
        Path = $file.FullName
        RelativePath = $relativePath
    }
    Write-Host "   [$index] $relativePath" -ForegroundColor White
    $index++
}

Write-Host ""
$selection = Read-Host "Enter the number of the file to restore (or 'q' to quit)"

if ($selection -eq 'q') {
    Write-Host "`n❌ Restore cancelled." -ForegroundColor Yellow
    exit 0
}

$selectedIndex = [int]$selection

if (!$fileList.ContainsKey($selectedIndex)) {
    Write-Host "`n❌ Invalid selection!" -ForegroundColor Red
    exit 1
}

$selectedFile = $fileList[$selectedIndex]
$sourcePath = $selectedFile.Path
$relativePath = $selectedFile.RelativePath
$destination = Join-Path $projectRoot $relativePath

Write-Host "`n📋 File to Restore:" -ForegroundColor Cyan
Write-Host "   From: $relativePath" -ForegroundColor White
Write-Host "   To:   $relativePath" -ForegroundColor White

$confirm = Read-Host "`n⚠️  This will overwrite the current version. Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "`n❌ Restore cancelled." -ForegroundColor Yellow
    exit 0
}

try {
    # Ensure destination directory exists
    $destDir = Split-Path $destination -Parent
    if (!(Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    # Copy file
    Copy-Item -Path $sourcePath -Destination $destination -Force
    Write-Host "`n✅ File restored successfully!" -ForegroundColor Green
    Write-Host "   Location: $destination" -ForegroundColor White
}
catch {
    Write-Host "`n❌ Error restoring file: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
