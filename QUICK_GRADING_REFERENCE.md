# 🎓 Quick Grading Scale Reference
## ✅ Official 10-Point University Grading Scale

## 📊 Point to Percentage Conversion

```
┌─────────────┬──────────────┬────────────────────┐
│ Point Grade │ Percentage   │ Description        │
├─────────────┼──────────────┼────────────────────┤
│    1.0      │   96-100%    │ ⭐ Excellent       │
│    1.25     │   93-95%     │ ⭐ Very Good       │
│    1.5      │   90-92%     │ ⭐ Good            │
│    1.75     │   87-89%     │ ⭐ Satisfactory    │ ← Merit Cutoff
│    2.0      │   84-86%     │ ✓ Fair             │
│    2.25     │   81-83%     │ ✓ Average          │ ← Basic Cutoff
│    2.5      │   78-80%     │ ⚠ Below Average    │
│    2.75     │   75-77%     │ ⚠ Passing          │
│    3.0      │   70-74%     │ ⚠ Minimum Passing  │
│    5.0      │   Below 70%  │ ❌ Failing         │
└─────────────┴──────────────┴────────────────────┘
```

**Conversion Method**: Midpoint of percentage ranges with linear interpolation

---

## 💰 Allowance Eligibility

### Merit Incentive (₱5,000)
- **Required**: ≥88% (GWA ≤1.75)
- **Examples**:
  - ✅ 1.0 = 98% → **ELIGIBLE**
  - ✅ 1.25 = 94% → **ELIGIBLE**
  - ✅ 1.5 = 91% → **ELIGIBLE**
  - ✅ 1.74 = 88.12% → **ELIGIBLE**
  - ✅ 1.75 = 88% → **ELIGIBLE** (exactly at cutoff)
  - ❌ 1.76 = 87.88% → **NOT ELIGIBLE** (below 88%)
  - ❌ 2.0 = 85% → **NOT ELIGIBLE**

### Basic Allowance (₱5,000)
- **Required**: ≥80% (GWA ≤2.25)
- **Examples**:
  - ✅ 1.75 = 88% → **ELIGIBLE**
  - ✅ 2.0 = 85% → **ELIGIBLE**
  - ✅ 2.25 = 82% → **ELIGIBLE** (exactly at cutoff)
  - ❌ 2.26 = 81.88% → **NOT ELIGIBLE** (below 80%)
  - ❌ 2.5 = 79% → **NOT ELIGIBLE**
  - ❌ 3.0 = 72% → **NOT ELIGIBLE**

### Both Merit + Basic (₱10,000)
- **GWA ≤1.75** gets both incentives!
- Total: ₱5,000 (Merit) + ₱5,000 (Basic) = **₱10,000**

---

## 📝 How to Submit Grades

1. **Login** to your student account
2. Go to **Grade Submission** form
3. Select **Semester** and **Academic Year**
4. Enter **GWA in point scale** (e.g., 1.75, 2.50)
5. Click **"View Grading Scale Reference"** if needed
6. Click **Submit**

**Note**: SWA (Semestral Weighted Average) is no longer required!

---

## ⚡ Quick Examples

### Example 1: Dean's Lister (Merit + Basic)
```
GWA: 1.5
→ Converts to: 91% (90-92 range)
→ Merit: ✅ Yes (91% ≥ 88%)
→ Basic: ✅ Yes (91% ≥ 80%)
→ Total Allowance: ₱10,000
```

### Example 2: Merit Cutoff (Exactly at threshold)
```
GWA: 1.75
→ Converts to: 88% (87-89 range)
→ Merit: ✅ Yes (88% ≥ 88%)
→ Basic: ✅ Yes (88% ≥ 80%)
→ Total Allowance: ₱10,000
```

### Example 3: Just Below Merit (Basic Only)
```
GWA: 1.76
→ Converts to: 87.88%
→ Merit: ❌ No (87.88% < 88%)
→ Basic: ✅ Yes (87.88% ≥ 80%)
→ Total Allowance: ₱5,000
```

### Example 4: Basic Cutoff
```
GWA: 2.25
→ Converts to: 82% (81-83 range)
→ Merit: ❌ No (82% < 88%)
→ Basic: ✅ Yes (82% ≥ 80%)
→ Total Allowance: ₱5,000
```

### Example 5: Below All Thresholds
```
GWA: 2.5
→ Converts to: 79% (78-80 range)
→ Merit: ❌ No (79% < 88%)
→ Basic: ❌ No (79% < 80%)
→ Total Allowance: ₱0
```

---

## 🔧 For Developers

### Conversion Function (Python)
```python
def _convert_to_percentage(gwa):
    # Official 10-point university grading scale
    conversion_table = [
        (1.0, 98.0),    # 96-100 → Excellent
        (1.25, 94.0),   # 93-95 → Very Good
        (1.5, 91.0),    # 90-92 → Good
        (1.75, 88.0),   # 87-89 → Satisfactory (MERIT CUTOFF)
        (2.0, 85.0),    # 84-86 → Fair
        (2.25, 82.0),   # 81-83 → Average (BASIC CUTOFF)
        (2.5, 79.0),    # 78-80 → Below Average
        (2.75, 76.0),   # 75-77 → Passing
        (3.0, 72.0),    # 70-74 → Minimum Passing
        (5.0, 40.0),    # Below 70 → Failing
    ]
    
    # Exact match
    for grade_point, percentage in conversion_table:
        if abs(gwa - grade_point) < 0.001:
            return percentage
    
    # Linear interpolation for intermediate values
    for i in range(len(conversion_table) - 1):
        g1, p1 = conversion_table[i]
        g2, p2 = conversion_table[i + 1]
        if g1 <= gwa <= g2:
            return p1 + (p2 - p1) * (gwa - g1) / (g2 - g1)
    
    return 40.0  # Below 5.0
```

### Eligibility Checks
```python
# Convert GWA to percentage
swa_percent = _convert_to_percentage(gwa)

# Check eligibility
merit_eligible = swa_percent >= 88.0  # GWA ≤1.75
basic_eligible = swa_percent >= 80.0  # GWA ≤2.25
```

### API Request Example
```json
{
  "semester": "1st Semester",
  "academic_year": "2023-2024",
  "general_weighted_average": 1.75
}
```

### API Response
```json
{
  "id": 123,
  "general_weighted_average": "1.75",
  "semestral_weighted_average": "1.75",  // Auto-filled
  "gwa_percentage": "88.00",
  "is_eligible_basic": true,
  "is_eligible_merit": true
}
```

---

## ❓ FAQs

**Q: What if my GWA is 1.85 (not in the official table)?**  
A: The system accepts ANY decimal format! Enter 1.85 exactly. The system will use linear interpolation:
- 1.85 is between 1.75 (88%) and 2.0 (85%)
- Calculated as: 88 + (85-88) × (1.85-1.75)/(2.0-1.75) = **86.8%**
- Result: Basic only (86.8% ≥ 80% but < 88%)

**Q: Can I enter "1" instead of "1.0"?**  
A: Yes! All these formats work: `1`, `1.0`, `1.00`, `1.75`, `1.91`

**Q: What's the difference between Merit and Basic?**  
A: 
- **Merit**: ≥88% (GWA ≤1.75) = Dean's Lister level = ₱5,000
- **Basic**: ≥80% (GWA ≤2.25) = Good standing = ₱5,000
- **Both**: If you get Merit, you automatically get Basic too = **₱10,000 total**

**Q: Why did my GWA 1.74 change from "not eligible" to "eligible"?**  
A: The university updated the grading scale! Old merit threshold was 87%, new threshold is 88%. Your 1.74 converts to 88.12%, so you now qualify for both Merit + Basic!

**Q: What happened to SWA (Semestral Weighted Average)?**  
A: The form still accepts it, but it's auto-filled from GWA now. Just enter your GWA.

**Q: Can I submit grades multiple times for the same semester?**  
A: No. You'll get an error: _"You have already submitted grades for 2024-2025 1st semester"_. Contact admin if you need to update.

**Q: How accurate is the conversion?**  
A: The system uses the **official university grading scale** with midpoint conversion (e.g., 1.75 = 88% from 87-89 range). Intermediate values use linear interpolation for mathematical precision.

---

**Need Help?** 
- Contact the admin for grade updates
- Check `NEW_10POINT_GRADING_SCALE_COMPLETE.md` for full technical details
- See `QUICK_COMMIT_GUIDE.md` for development workflow
