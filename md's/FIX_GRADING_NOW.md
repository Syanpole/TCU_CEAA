# ⚡ QUICK COMMAND - Fix Grading Eligibility

## Run This Command:

```powershell
.\fix_grade_eligibility_final.ps1
```

OR

```bash
cd backend
python manage.py fix_grade_eligibility_final
```

## What It Does:

Updates all grade submissions to use the correct criteria:
- **GWA 1.0-1.75** = ₱10,000 (Basic + Merit)
- **GWA 1.76-2.5** = ₱5,000 (Basic only)
- **GWA 2.51+** = ₱0 (Not eligible)

## Status: ✅ COMPLETE

All submissions already using correct criteria!

---
**80% (GWA 2.5) is the minimum for Basic Allowance**
