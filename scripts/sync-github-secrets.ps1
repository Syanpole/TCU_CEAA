# ============================================================================
# GitHub Secrets Documentation & Helper
# ============================================================================
# This file documents what secrets need to be set in GitHub Actions
# for CI/CD pipeline to work properly
# ============================================================================

# Your current backend/.env secrets that need to be added to GitHub:

## 🗄️ DATABASE SECRETS (for CI tests)
# These are already configured in ci.yml to use test values:
# - POSTGRES_DB: test_tcu_ceaa (hardcoded in workflow)
# - POSTGRES_USER: postgres (hardcoded)
# - POSTGRES_PASSWORD: postgres (hardcoded)

## 🔑 DJANGO SECRETS
# Add these to GitHub repository secrets:
# SECRET_KEY=4j4nn_duol6j(qbjrg(a1pbk%3d_olvw9^!%z+kdp*jop7&^+4

## ☁️ AWS SECRETS (for S3 and Textract)
# Add these to GitHub repository secrets:
# AWS_ACCESS_KEY_ID=AKIAWZNMCNNJEXB7DKWK
# AWS_SECRET_ACCESS_KEY=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
# AWS_STORAGE_BUCKET_NAME=tcu-ceaa-documents
# AWS_S3_REGION_NAME=us-east-1

## 📧 EMAIL SECRETS
# Add these to GitHub repository secrets:
# EMAIL_HOST_USER=tcu.ceaa.scholarships@gmail.com
# EMAIL_HOST_PASSWORD=exwgtsexjmwudjvl

## 🐳 DOCKER REGISTRY SECRETS (for deployment)
# Add these to GitHub repository secrets:
# DOCKER_REGISTRY=your-registry-url (e.g., your-aws-account-id.dkr.ecr.us-east-1.amazonaws.com)
# DOCKER_USERNAME=your-username (or AWS access key for ECR)
# DOCKER_PASSWORD=your-password (or AWS secret key for ECR)

## ☸️ KUBERNETES SECRETS (for deployment)
# Add these to GitHub repository secrets:
# KUBECONFIG_DATA=<base64 encoded kubeconfig file>

# ============================================================================
# HOW TO ADD SECRETS TO GITHUB
# ============================================================================
# 1. Go to: https://github.com/Syanpole/TCU_CEAA/settings/secrets/actions
# 2. Click "New repository secret"
# 3. Add each secret from above
# 4. Save

# ============================================================================
# POWERSHELL SCRIPT TO GENERATE GITHUB SECRETS COMMANDS
# ============================================================================

Write-Host "🔐 GitHub Secrets Configuration Helper" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Note: GitHub CLI (gh) is required for automated setup" -ForegroundColor Yellow
Write-Host "   Install: https://cli.github.com/" -ForegroundColor Gray
Write-Host ""

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghInstalled) {
    Write-Host "❌ GitHub CLI (gh) not installed" -ForegroundColor Red
    Write-Host "   Install from: https://cli.github.com/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Manual setup instructions:" -ForegroundColor Cyan
    Write-Host "   1. Go to: https://github.com/Syanpole/TCU_CEAA/settings/secrets/actions" -ForegroundColor Gray
    Write-Host "   2. Click 'New repository secret'" -ForegroundColor Gray
    Write-Host "   3. Add each secret below:" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✅ GitHub CLI installed" -ForegroundColor Green
    Write-Host ""
    
    # Check if authenticated
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Not authenticated with GitHub" -ForegroundColor Red
        Write-Host "   Run: gh auth login" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host "✅ Authenticated with GitHub" -ForegroundColor Green
        Write-Host ""
    }
}

# Read .env file
$envFile = "..\backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env file not found: $envFile" -ForegroundColor Red
    exit 1
}

Write-Host "📄 Reading secrets from: $envFile" -ForegroundColor Green
Write-Host ""

# Parse .env file
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            $envVars[$key] = $value
        }
    }
}

# Secrets to add to GitHub
$githubSecrets = @{
    "SECRET_KEY" = $envVars["SECRET_KEY"]
    "AWS_ACCESS_KEY_ID" = $envVars["AWS_ACCESS_KEY_ID"]
    "AWS_SECRET_ACCESS_KEY" = $envVars["AWS_SECRET_ACCESS_KEY"]
    "AWS_STORAGE_BUCKET_NAME" = $envVars["AWS_STORAGE_BUCKET_NAME"]
    "AWS_S3_REGION_NAME" = $envVars["AWS_S3_REGION_NAME"]
    "EMAIL_HOST_USER" = $envVars["EMAIL_HOST_USER"]
    "EMAIL_HOST_PASSWORD" = $envVars["EMAIL_HOST_PASSWORD"]
}

Write-Host "🔑 Secrets to add to GitHub Actions:" -ForegroundColor Yellow
Write-Host ""

$secretCount = 0
foreach ($key in $githubSecrets.Keys) {
    $value = $githubSecrets[$key]
    if ([string]::IsNullOrWhiteSpace($value)) {
        Write-Host "   ⚠️  $key (missing in .env)" -ForegroundColor Yellow
    } else {
        $secretCount++
        $maskedValue = if ($value.Length -gt 8) { 
            $value.Substring(0, 4) + "****" + $value.Substring($value.Length - 4) 
        } else { 
            "****" 
        }
        Write-Host "   ✓ $key = $maskedValue" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📊 Found $secretCount secrets" -ForegroundColor Green
Write-Host ""

if ($ghInstalled -and (gh auth status 2>&1 | Select-String -Pattern "Logged in")) {
    Write-Host "🚀 Ready to upload secrets to GitHub!" -ForegroundColor Green
    Write-Host ""
    
    $response = Read-Host "Do you want to upload these secrets to GitHub now? (y/N)"
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host ""
        Write-Host "📤 Uploading secrets to GitHub..." -ForegroundColor Yellow
        Write-Host ""
        
        foreach ($key in $githubSecrets.Keys) {
            $value = $githubSecrets[$key]
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                try {
                    # Use gh secret set
                    $value | gh secret set $key --repo Syanpole/TCU_CEAA
                    Write-Host "   ✅ $key uploaded" -ForegroundColor Green
                } catch {
                    Write-Host "   ❌ Failed to upload $key : $_" -ForegroundColor Red
                }
            }
        }
        
        Write-Host ""
        Write-Host "✨ Done! Secrets uploaded to GitHub." -ForegroundColor Green
        Write-Host ""
        Write-Host "🔍 Verify at: https://github.com/Syanpole/TCU_CEAA/settings/secrets/actions" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "⏭️  Skipped. You can run this script again later." -ForegroundColor Yellow
    }
} else {
    Write-Host "📋 Manual commands (run these if you have GitHub CLI):" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($key in $githubSecrets.Keys) {
        $value = $githubSecrets[$key]
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            Write-Host "   echo `"$value`" | gh secret set $key --repo Syanpole/TCU_CEAA" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "📝 Additional secrets you may need to add manually:" -ForegroundColor Yellow
Write-Host "   - DOCKER_REGISTRY (your container registry URL)" -ForegroundColor Gray
Write-Host "   - DOCKER_USERNAME (for registry authentication)" -ForegroundColor Gray
Write-Host "   - DOCKER_PASSWORD (for registry authentication)" -ForegroundColor Gray
Write-Host "   - KUBECONFIG_DATA (base64 encoded kubeconfig for deployment)" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Done!" -ForegroundColor Green
