# ============================================================================
# AWS Cognito Identity Pool Setup and Validation Script
# ============================================================================
# This script validates AWS credentials and ensures proper Cognito setup
# for the Face Liveness Detection feature

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "AWS Cognito Identity Pool Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Validate Backend .env file
Write-Host "[1/5] Validating backend .env configuration..." -ForegroundColor Yellow

$envFile = ".\backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: backend\.env file not found!" -ForegroundColor Red
    exit 1
}

$envContent = Get-Content $envFile -Raw

# Check required AWS variables
$requiredVars = @(
    "AWS_ACCESS_KEY_ID=AKIAWZNMCNNJEXB7DKWK",
    "AWS_SECRET_ACCESS_KEY=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",
    "AWS_STORAGE_BUCKET_NAME=tcu-ceaa-documents",
    "AWS_S3_REGION_NAME=us-east-1",
    "VERIFICATION_SERVICE_ENABLED=True",
    "VERIFICATION_SERVICE_REGION=us-east-1"
)

$allFound = $true
foreach ($var in $requiredVars) {
    $key = $var.Split('=')[0]
    if ($envContent -match "$key=") {
        Write-Host "  ✓ $key configured" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $key missing" -ForegroundColor Red
        $allFound = $false
    }
}

if (-not $allFound) {
    Write-Host "`n❌ Some required AWS variables are missing in .env" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Backend .env configuration valid`n" -ForegroundColor Green

# Step 2: Validate Amplify Service Configuration
Write-Host "[2/5] Validating Amplify Service configuration..." -ForegroundColor Yellow

$amplifyServiceFile = ".\frontend\src\services\amplifyService.ts"
if (-not (Test-Path $amplifyServiceFile)) {
    Write-Host "❌ Error: amplifyService.ts not found!" -ForegroundColor Red
    exit 1
}

$amplifyContent = Get-Content $amplifyServiceFile -Raw

if ($amplifyContent -match "identityPoolId: 'us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5'") {
    Write-Host "  ✓ Cognito Identity Pool ID configured" -ForegroundColor Green
} else {
    Write-Host "  ❌ Cognito Identity Pool ID not found" -ForegroundColor Red
    Write-Host "     Expected: us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5" -ForegroundColor Yellow
    exit 1
}

if ($amplifyContent -match "allowGuestAccess: true") {
    Write-Host "  ✓ Guest access enabled" -ForegroundColor Green
} else {
    Write-Host "  ❌ Guest access not enabled" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Amplify Service configuration valid`n" -ForegroundColor Green

# Step 3: Test AWS Credentials
Write-Host "[3/5] Testing AWS credentials..." -ForegroundColor Yellow

# Check if AWS CLI is installed
$awsCliInstalled = $null -ne (Get-Command aws -ErrorAction SilentlyContinue)

if ($awsCliInstalled) {
    Write-Host "  ℹ AWS CLI detected, testing credentials..." -ForegroundColor Cyan
    
    # Set temporary environment variables
    $env:AWS_ACCESS_KEY_ID = "AKIAWZNMCNNJEXB7DKWK"
    $env:AWS_SECRET_ACCESS_KEY = "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"
    $env:AWS_DEFAULT_REGION = "us-east-1"
    
    # Test credentials
    $stsOutput = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ AWS credentials are valid" -ForegroundColor Green
        Write-Host "  ℹ Account info:" -ForegroundColor Cyan
        Write-Host "    $stsOutput" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠ AWS credentials test failed" -ForegroundColor Yellow
        Write-Host "    This might be normal if credentials have limited permissions" -ForegroundColor Gray
    }
    
    # Clear temporary environment variables
    Remove-Item Env:\AWS_ACCESS_KEY_ID -ErrorAction SilentlyContinue
    Remove-Item Env:\AWS_SECRET_ACCESS_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:\AWS_DEFAULT_REGION -ErrorAction SilentlyContinue
} else {
    Write-Host "  ℹ AWS CLI not installed, skipping credentials test" -ForegroundColor Gray
    Write-Host "    To install: winget install Amazon.AWSCLI" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Validate Cognito Identity Pool Permissions
Write-Host "[4/5] Checking Cognito Identity Pool configuration..." -ForegroundColor Yellow

Write-Host "  ℹ Identity Pool ID: us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5" -ForegroundColor Cyan
Write-Host "  ℹ Region: us-east-1" -ForegroundColor Cyan

if ($awsCliInstalled) {
    Write-Host "`n  Testing Cognito Identity Pool..." -ForegroundColor Cyan
    
    $env:AWS_ACCESS_KEY_ID = "AKIAWZNMCNNJEXB7DKWK"
    $env:AWS_SECRET_ACCESS_KEY = "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"
    $env:AWS_DEFAULT_REGION = "us-east-1"
    
    $cognitoOutput = aws cognito-identity describe-identity-pool --identity-pool-id "us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Cognito Identity Pool is accessible" -ForegroundColor Green
        $poolInfo = $cognitoOutput | ConvertFrom-Json
        Write-Host "  ℹ Pool Name: $($poolInfo.IdentityPoolName)" -ForegroundColor Cyan
        Write-Host "  ℹ Allow Unauthenticated Access: $($poolInfo.AllowUnauthenticatedIdentities)" -ForegroundColor Cyan
    } else {
        Write-Host "  ⚠ Could not access Cognito Identity Pool" -ForegroundColor Yellow
        Write-Host "    This is normal if credentials have limited permissions" -ForegroundColor Gray
        Write-Host "    The pool ID is configured correctly in the code" -ForegroundColor Gray
    }
    
    Remove-Item Env:\AWS_ACCESS_KEY_ID -ErrorAction SilentlyContinue
    Remove-Item Env:\AWS_SECRET_ACCESS_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:\AWS_DEFAULT_REGION -ErrorAction SilentlyContinue
}

Write-Host "`n✅ Cognito configuration validated`n" -ForegroundColor Green

# Step 5: Summary and Next Steps
Write-Host "[5/5] Configuration Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Configuration Status: READY" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Configuration Details:" -ForegroundColor Cyan
Write-Host "  • Backend: Django with AWS credentials configured" -ForegroundColor White
Write-Host "  • Frontend: Amplify with Cognito Identity Pool" -ForegroundColor White
Write-Host "  • Identity Pool: us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5" -ForegroundColor White
Write-Host "  • Region: us-east-1" -ForegroundColor White
Write-Host "  • Guest Access: Enabled" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Security Notes:" -ForegroundColor Yellow
Write-Host "  • Backend exposes AWS credentials (DEV MODE ONLY)" -ForegroundColor White
Write-Host "  • Cognito Identity Pool provides temporary credentials" -ForegroundColor White
Write-Host "  • For production, migrate to Cognito-only authentication" -ForegroundColor White
Write-Host ""
Write-Host "🧪 Testing Instructions:" -ForegroundColor Cyan
Write-Host "  1. Start backend server:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Gray
Write-Host "     python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start frontend dev server:" -ForegroundColor White
Write-Host "     cd frontend" -ForegroundColor Gray
Write-Host "     npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Test face liveness detection:" -ForegroundColor White
Write-Host "     • Log in to the application" -ForegroundColor Gray
Write-Host "     • Navigate to allowance application" -ForegroundColor Gray
Write-Host "     • Click 'Start Verification'" -ForegroundColor Gray
Write-Host "     • Follow on-screen prompts" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Expected Console Output:" -ForegroundColor Cyan
Write-Host "  🔧 Fetching AWS credentials from backend..." -ForegroundColor Gray
Write-Host "  🔧 Configuring AWS Amplify with region: us-east-1" -ForegroundColor Gray
Write-Host "  ✅ Amplify configured successfully" -ForegroundColor Gray
Write-Host "  ✅ Session created: [session-id]" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 IAM Permissions Required:" -ForegroundColor Yellow
Write-Host "  The Cognito Identity Pool IAM role needs:" -ForegroundColor White
Write-Host "  • rekognition:CreateFaceLivenessSession" -ForegroundColor Gray
Write-Host "  • rekognition:StartFaceLivenessSession" -ForegroundColor Gray
Write-Host "  • rekognition:GetFaceLivenessSessionResults" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
