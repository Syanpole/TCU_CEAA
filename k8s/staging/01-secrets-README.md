# ⚠️ IMPORTANT: Kubernetes Secrets Management

## 🚫 DO NOT commit real secrets to Git!

This file contains your **actual credentials**. It should be:
- ✅ Generated locally using `scripts/generate-k8s-secrets.ps1`
- ✅ Applied directly to your Kubernetes cluster
- ❌ **NEVER committed to Git**

## 📝 How to use:

### 1. Generate secrets from your .env file:
```powershell
cd scripts
.\generate-k8s-secrets.ps1 -Environment staging
```

### 2. The script will create this file with your real credentials

### 3. Apply to Kubernetes:
```bash
kubectl apply -f k8s/staging/01-secrets.yaml
```

### 4. Verify:
```bash
kubectl get secrets -n tcu-ceaa-staging
```

## 🔐 Security Notes:

- This file is in `.gitignore` - it will not be committed
- The template file in Git contains placeholder values only
- Your real credentials stay in `backend/.env` (also in `.gitignore`)
- Each developer/server generates their own secrets locally

## 📚 More Info:

See `SECRETS_MANAGEMENT_GUIDE.md` for complete documentation.
