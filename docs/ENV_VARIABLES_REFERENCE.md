# Environment Variables Quick Reference

This document explains how database configuration works in both CI and local development environments.

## Priority Order

The Django application reads database credentials in the following priority order:

1. **`POSTGRES_*` variables** (CI standard, highest priority)
2. **`DB_*` variables** (local development, fallback)  
3. **Hard-coded defaults** (last resort)

## Environment Variable Mapping

| Setting | Priority 1 (CI) | Priority 2 (Local) | Default Value |
|---------|----------------|--------------------|--------------:|
| **Database Name** | `POSTGRES_DB` | `DB_NAME` | `tcu_ceaa_database` |
| **Database User** | `POSTGRES_USER` | `DB_USER` | `postgres` |
| **Database Password** | `POSTGRES_PASSWORD` | `DB_PASSWORD` | `TCU@ADMIN!scholarship` |
| **Database Host** | `DATABASE_HOST` | `DB_HOST` | `localhost` |
| **Database Port** | `DATABASE_PORT` | `DB_PORT` | `5432` |

## Usage Examples

### CI Environment (GitHub Actions)

```yaml
env:
  POSTGRES_DB: test_tcu_ceaa
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  DATABASE_HOST: localhost
  DATABASE_PORT: 5432
```

**Result**: Django uses `POSTGRES_*` variables directly from the CI workflow.

### Local Development (.env file)

```properties
DB_NAME=tcu_ceaa_db
DB_USER=postgres
DB_PASSWORD=admin123
DB_HOST=localhost
DB_PORT=5432
```

**Result**: Django falls back to `DB_*` variables from your local `.env` file.

### Testing Locally with CI Settings

**Windows PowerShell:**
```powershell
$env:POSTGRES_DB="test_tcu_ceaa"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="postgres"
$env:DATABASE_HOST="localhost"
$env:DATABASE_PORT="5432"
cd backend
python manage.py test
```

**Linux/Mac:**
```bash
export POSTGRES_DB=test_tcu_ceaa
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
cd backend
python manage.py test
```

## Why This Design?

✅ **Standardization**: Uses PostgreSQL's standard `POSTGRES_*` convention in CI  
✅ **Compatibility**: Maintains backwards compatibility with existing `DB_*` variables  
✅ **Flexibility**: Supports both CI and local development without conflicts  
✅ **Robustness**: Multiple fallback levels prevent configuration errors  

## Testing the Configuration

Run the configuration test to verify everything works:

```bash
cd backend
python test_database_config.py
```

Expected output: `✅ All tests passed!`

## Troubleshooting

### Issue: "FATAL: role 'root' does not exist"
**Cause**: Using incorrect database user  
**Solution**: Ensure `POSTGRES_USER=postgres` is set in CI environment

### Issue: Database connection refused
**Cause**: Incorrect host or port  
**Solution**: Verify `DATABASE_HOST=localhost` and `DATABASE_PORT=5432`

### Issue: Authentication failed
**Cause**: Password mismatch  
**Solution**: Ensure `POSTGRES_PASSWORD` matches PostgreSQL service configuration

## For Developers

No changes needed to your local `.env` file! The existing `DB_*` variables will continue to work as before. The new `POSTGRES_*` support is primarily for CI consistency.

## For CI/CD

The GitHub Actions workflow now sets both variable conventions for maximum compatibility:
- `POSTGRES_*` for PostgreSQL service alignment
- `DB_*` for backwards compatibility

This ensures the Django application can connect regardless of which convention is used.
