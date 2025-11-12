# Generate Kubernetes Secrets from .env file
param(
    [string]$Environment = "staging"
)

Write-Host "🔐 Generating Kubernetes Secrets for $Environment" -ForegroundColor Cyan
Write-Host ""

# Read .env file
$envFile = "..\backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

# Parse .env
$env = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Count -eq 2) {
            $env[$parts[0].Trim()] = $parts[1].Trim()
        }
    }
}

Write-Host "✅ Found secrets in .env" -ForegroundColor Green

# Base64 encode function
function ToBase64($text) {
    return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($text))
}

# Set environment values
if ($Environment -eq "staging") {
    $ns = "tcu-ceaa-staging"
    $db = "tcu_ceaa_staging"
    $bucket = "tcu-ceaa-staging-media"
} else {
    $ns = "tcu-ceaa"
    $db = "tcu_ceaa"
    $bucket = "tcu-ceaa-media"
}

# Encode secrets
$dbPasswordB64 = ToBase64 $env["DB_PASSWORD"]
$secretKeyB64 = ToBase64 $env["SECRET_KEY"]
$awsKeyB64 = ToBase64 $env["AWS_ACCESS_KEY_ID"]
$awsSecretB64 = ToBase64 $env["AWS_SECRET_ACCESS_KEY"]
$bucketB64 = ToBase64 $bucket
$regionB64 = ToBase64 $env["AWS_S3_REGION_NAME"]
$emailUserB64 = ToBase64 $env["EMAIL_HOST_USER"]
$emailPassB64 = ToBase64 $env["EMAIL_HOST_PASSWORD"]
$dbB64 = ToBase64 $db
$userB64 = ToBase64 "postgres"

# Create YAML (part 1 - Secret)
$yaml = "apiVersion: v1`n"
$yaml += "kind: Secret`n"
$yaml += "metadata:`n"
$yaml += "  name: tcu-ceaa-secrets`n"
$yaml += "  namespace: $ns`n"
$yaml += "type: Opaque`n"
$yaml += "data:`n"
$yaml += "  POSTGRES_DB: $dbB64`n"
$yaml += "  POSTGRES_USER: $userB64`n"
$yaml += "  POSTGRES_PASSWORD: $dbPasswordB64`n"
$yaml += "  SECRET_KEY: $secretKeyB64`n"
$yaml += "  AWS_ACCESS_KEY_ID: $awsKeyB64`n"
$yaml += "  AWS_SECRET_ACCESS_KEY: $awsSecretB64`n"
$yaml += "  AWS_STORAGE_BUCKET_NAME: $bucketB64`n"
$yaml += "  AWS_S3_REGION_NAME: $regionB64`n"
$yaml += "  EMAIL_HOST_USER: $emailUserB64`n"
$yaml += "  EMAIL_HOST_PASSWORD: $emailPassB64`n"

# ConfigMap
$yaml += "`n---`n"
$yaml += "apiVersion: v1`n"
$yaml += "kind: ConfigMap`n"
$yaml += "metadata:`n"
$yaml += "  name: tcu-ceaa-config`n"
$yaml += "  namespace: $ns`n"
$yaml += "data:`n"
$yaml += "  DEBUG: `"False`"`n"
if ($Environment -eq "staging") {
    $yaml += "  ALLOWED_HOSTS: `"staging.tcu-ceaa.com`"`n"
    $yaml += "  FRONTEND_URL: `"http://staging.tcu-ceaa.com`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_COE: `"True`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_ID: `"True`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_BIRTH_CERT: `"False`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_VOTERS: `"False`"`n"
    $yaml += "  FEATURE_LIVENESS_CHECK: `"False`"`n"
} else {
    $yaml += "  ALLOWED_HOSTS: `"tcu-ceaa.com,api.tcu-ceaa.com`"`n"
    $yaml += "  FRONTEND_URL: `"https://tcu-ceaa.com`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_COE: `"True`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_ID: `"True`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_BIRTH_CERT: `"True`"`n"
    $yaml += "  FEATURE_AUTO_VERIFY_VOTERS: `"True`"`n"
    $yaml += "  FEATURE_LIVENESS_CHECK: `"True`"`n"
}
$yaml += "  USE_CLOUD_STORAGE: `"True`"`n"
$yaml += "  USE_ADVANCED_OCR: `"True`"`n"
$yaml += "  EMAIL_BACKEND: `"django.core.mail.backends.smtp.EmailBackend`"`n"
$yaml += "  EMAIL_HOST: `"smtp.gmail.com`"`n"
$yaml += "  EMAIL_PORT: `"587`"`n"
$yaml += "  EMAIL_USE_TLS: `"True`"`n"

# Write file
$outFile = "..\k8s\$Environment\01-secrets.yaml"
$yaml | Out-File -FilePath $outFile -Encoding UTF8 -Force

Write-Host ""
Write-Host "✅ Generated: $outFile" -ForegroundColor Green
Write-Host "   Namespace: $ns" -ForegroundColor Gray
Write-Host "   Database: $db" -ForegroundColor Gray
Write-Host "   S3 Bucket: $bucket" -ForegroundColor Gray
Write-Host ""
Write-Host "📦 Next:" -ForegroundColor Yellow
Write-Host "   kubectl apply -f $outFile" -ForegroundColor Gray
Write-Host ""
