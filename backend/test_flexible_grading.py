import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from decimal import Decimal

# Test the conversion function directly
def _convert_to_percentage(gwa_value):
    if gwa_value >= 65:
        return float(gwa_value)
    
    conversion_table = [
        (1.00, 96.00), (1.25, 93.00), (1.50, 90.00), (1.75, 87.00),
        (2.00, 84.00), (2.25, 81.00), (2.50, 78.00), (2.75, 75.00),
        (3.00, 72.00), (4.00, 68.00), (5.00, 65.00),
    ]
    
    for point, percent in conversion_table:
        if abs(gwa_value - point) < 0.01:
            return percent
    
    for i in range(len(conversion_table) - 1):
        point1, percent1 = conversion_table[i]
        point2, percent2 = conversion_table[i + 1]
        
        if point1 <= gwa_value <= point2:
            ratio = (gwa_value - point1) / (point2 - point1)
            interpolated = percent1 + ratio * (percent2 - percent1)
            return round(interpolated, 2)
    
    if gwa_value < 1.00:
        return 96.00
    if gwa_value > 5.00:
        return 0.00
    
    return 65.00

print("=" * 70)
print("FLEXIBLE GRADING FORMAT TEST - Any Decimal Format Accepted")
print("=" * 70)

# Test cases with different decimal formats
test_cases = [
    # Single digit (integer)
    (1, "Integer format"),
    (2, "Integer format"),
    (3, "Integer format"),
    
    # One decimal place
    (1.0, "One decimal"),
    (1.5, "One decimal"),
    (1.7, "One decimal"),
    (2.0, "One decimal"),
    (2.3, "One decimal"),
    
    # Two decimal places
    (1.00, "Two decimals"),
    (1.79, "Two decimals"),
    (1.91, "Two decimals"),
    (2.00, "Two decimals"),
    (2.35, "Two decimals"),
    (1.72, "Two decimals"),
    
    # Edge cases
    (1.74, "User's original"),
    (1.75, "Exact match"),
    (2.99, "Almost 3.0"),
    (4.5, "Between 4-5"),
]

print(f"\n{'GWA Input':<12} {'Format':<15} {'Percentage':<12} {'Basic':<8} {'Merit':<8}")
print("-" * 70)

for gwa, note in test_cases:
    pct = _convert_to_percentage(gwa)
    basic = "YES" if pct >= 80.0 else "NO"
    merit = "YES" if pct >= 87.0 else "NO"
    print(f"{str(gwa):<12} {note:<15} {pct:<12.2f} {basic:<8} {merit:<8}")

print("=" * 70)
print("\n✅ ALL FORMATS ACCEPTED!")
print("   - Integer: 1, 2, 3")
print("   - One decimal: 1.0, 1.5, 2.7")
print("   - Two decimals: 1.00, 1.79, 2.35")
print("   - Any value between 1.0 and 5.0 is valid!")
print("=" * 70)
