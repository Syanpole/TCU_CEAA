# Push Docker Images to AWS ECR
# Usage: .\scripts\push-images-to-ecr.ps1

$ErrorActionPreference = "Stop"

$REGISTRY = "466901691218.dkr.ecr.us-east-1.amazonaws.com"
$IMAGES = @("backend", "celery", "frontend")
$TAG = "staging"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Pushing Images to ECR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verify all images exist
Write-Host "Verifying all images are built..." -ForegroundColor Yellow
foreach ($image in $IMAGES) {
    $imageName = "$REGISTRY/tcu-ceaa/${image}:$TAG"
    $exists = docker images -q $imageName
    if ([string]::IsNullOrEmpty($exists)) {
        Write-Host "ERROR: Image not found: $imageName" -ForegroundColor Red
        Write-Host "Please build the image first." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Found: $image" -ForegroundColor Green
}

Write-Host ""
Write-Host "All images verified. Starting push..." -ForegroundColor Green
Write-Host ""

# Push each image
$totalImages = $IMAGES.Count
$currentImage = 0

foreach ($image in $IMAGES) {
    $currentImage++
    $imageName = "$REGISTRY/tcu-ceaa/${image}:$TAG"
    
    Write-Host "[$currentImage/$totalImages] Pushing $image..." -ForegroundColor Cyan
    Write-Host "Image: $imageName" -ForegroundColor Gray
    Write-Host ""
    
    $startTime = Get-Date
    docker push $imageName
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to push $image" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Successfully pushed $image (took $([math]::Round($duration, 1))s)" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All Images Pushed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update K8s manifests with registry URLs" -ForegroundColor White
Write-Host "2. Install eksctl and kubectl" -ForegroundColor White
Write-Host "3. Create EKS cluster" -ForegroundColor White
Write-Host "4. Deploy to Kubernetes" -ForegroundColor White
Write-Host ""
Write-Host "Run: Get-Content AWS_DEPLOYMENT_STEP_BY_STEP.md" -ForegroundColor Cyan
