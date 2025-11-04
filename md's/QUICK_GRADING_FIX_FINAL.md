# 🎓 TCU-CEAA GRADING - QUICK REFERENCE

## 📊 ELIGIBILITY AT A GLANCE

| GWA Range | Basic (₱5k) | Merit (₱5k) | Total |
|-----------|-------------|-------------|-------|
| 1.0 - 1.75 | ✅ | ✅ | **₱10,000** |
| 1.76 - 2.5 | ✅ | ❌ | **₱5,000** |
| 2.51+ | ❌ | ❌ | **₱0** |

## 🚀 RUN THE FIX (Choose One)

### Option 1: PowerShell Script
```powershell
.\fix_grade_eligibility_final.ps1
```

### Option 2: Django Command
```bash
cd backend
python manage.py fix_grade_eligibility_final --dry-run  # Preview first
python manage.py fix_grade_eligibility_final            # Apply fix
```

## ✅ VERIFY IT WORKS

1. **Run the command** (see above)
2. **Refresh student dashboard**
3. **Check grades page** - should show correct ✅/❌
4. **Test allowance application** - should show correct amounts

## 📋 EXAMPLES

- **GWA 1.5** → ✅ Basic + ✅ Merit = **₱10,000** ✅
- **GWA 1.75** → ✅ Basic + ✅ Merit = **₱10,000** ✅
- **GWA 2.0** → ✅ Basic + ❌ Merit = **₱5,000** ✅
- **GWA 2.5** → ✅ Basic + ❌ Merit = **₱5,000** ✅ (MINIMUM)
- **GWA 2.75** → ❌ Basic + ❌ Merit = **₱0** ✅
- **GWA 3.0** → ❌ Basic + ❌ Merit = **₱0** ✅

## 🔧 FILES CHANGED

- ✅ `backend/myapp/models.py` - Updated eligibility logic
- ✅ `backend/myapp/management/commands/fix_grade_eligibility_final.py` - Fix command
- ✅ `fix_grade_eligibility_final.ps1` - PowerShell helper
- ✅ `OFFICIAL_TCU_CEAA_GRADING_CRITERIA_FINAL.md` - Full documentation

## 📞 TROUBLESHOOTING

**Problem:** Old grades still wrong  
**Solution:** Run the management command

**Problem:** New submissions wrong  
**Solution:** Check backend/myapp/models.py has correct code

**Problem:** Command not found  
**Solution:** Make sure you're in the `backend` directory

---

**Status:** ✅ COMPLETE  
**Last Updated:** 2025-10-19  
**Version:** FINAL v3.0
