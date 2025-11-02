# ============================================
# Organize AI Template Documents
# ============================================
# This script helps organize your template documents
# into the correct AI reference folders

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "AI Template Document Organizer" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = "backend\ai_model_data\reference_documents"

# Template file mappings
$templates = @{
    "NSO_BIRTH_CERTIFICATE_TEMPLATE 1.jpg" = "birth_certificates"
    "CAS_ID_TEMPLATE 1.jpg" = "school_ids"
    "CBM_ID_TEMPLATE 1.jpg" = "school_ids"
    "CCI_ID_TEMPLATE 1.jpg" = "school_ids"
    "CICT_ID_TEMPLATE 1.jpg" = "school_ids"
    "VOTERS_CERTIFICATE_TEMPLATE 1.jpg" = "government_ids"
    "GENERAL_COE_FORMAT 1.jpg" = "certificates_of_enrollment"
    "GENERAL_COE_FORMAT 2.jpg" = "certificates_of_enrollment"
    "TOR_TEMPLATE 1.jpg" = "transcripts"
}

Write-Host "Checking current template locations..." -ForegroundColor Yellow
Write-Host ""

$moved = 0
$alreadyInPlace = 0
$notFound = 0

foreach ($file in $templates.Keys) {
    $targetFolder = $templates[$file]
    $targetPath = Join-Path $baseDir $targetFolder
    $targetFile = Join-Path $targetPath $file
    
    Write-Host "📄 $file" -ForegroundColor White
    
    # Check if file already exists in target location
    if (Test-Path $targetFile) {
        Write-Host "   ✅ Already in correct location: $targetFolder" -ForegroundColor Green
        $alreadyInPlace++
    } else {
        # Search for file in current directory and subdirectories
        $foundFiles = Get-ChildItem -Path . -Filter $file -Recurse -ErrorAction SilentlyContinue
        
        if ($foundFiles.Count -gt 0) {
            $sourceFile = $foundFiles[0].FullName
            Write-Host "   📁 Found at: $($foundFiles[0].Directory.Name)" -ForegroundColor Cyan
            Write-Host "   ➡️  Moving to: $targetFolder" -ForegroundColor Yellow
            
            # Create target directory if it doesn't exist
            if (-not (Test-Path $targetPath)) {
                New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
                Write-Host "   📂 Created directory: $targetFolder" -ForegroundColor Magenta
            }
            
            # Move the file
            try {
                Move-Item -Path $sourceFile -Destination $targetFile -Force
                Write-Host "   ✅ Successfully moved!" -ForegroundColor Green
                $moved++
            } catch {
                Write-Host "   ❌ Error moving file: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "   ⚠️  File not found in workspace" -ForegroundColor Red
            $notFound++
        }
    }
    Write-Host ""
}

# Summary
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "✅ Already in place: $alreadyInPlace" -ForegroundColor Green
Write-Host "➡️  Moved: $moved" -ForegroundColor Yellow
Write-Host "⚠️  Not found: $notFound" -ForegroundColor Red
Write-Host ""

# Show final directory structure
Write-Host "Final directory structure:" -ForegroundColor Cyan
Write-Host ""
Get-ChildItem -Path $baseDir -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Replace((Get-Location).Path, "").TrimStart('\')
    Write-Host "  📄 $relativePath" -ForegroundColor Gray
}
Write-Host ""

Write-Host "✅ Organization complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Your AI templates are now ready for use!" -ForegroundColor Cyan
Write-Host "The AI verification system will use these templates to validate submitted documents." -ForegroundColor Gray
Write-Host ""
