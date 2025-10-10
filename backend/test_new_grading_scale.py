"""
Test script for the new official 10-point grading scale

This script tests:
1. Official grade points (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 5.0)
2. Merit threshold at 1.75 (88%)
3. Basic threshold at 2.25 (80%)
4. Flexible decimal format support
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from decimal import Decimal
from myapp.models import GradeSubmission

def test_grading_scale():
    print("=" * 80)
    print("TESTING NEW OFFICIAL 10-POINT GRADING SCALE")
    print("=" * 80)
    
    # Test official grade points
    test_cases = [
        (1.0, 98.0, "Excellent", True, True),
        (1.25, 94.0, "Very Good", True, True),
        (1.5, 91.0, "Good", True, True),
        (1.75, 88.0, "Satisfactory", True, True),  # Merit cutoff
        (2.0, 85.0, "Fair", True, False),
        (2.25, 82.0, "Average", True, False),  # Basic cutoff
        (2.5, 79.0, "Below Average", False, False),
        (2.75, 76.0, "Passing", False, False),
        (3.0, 72.0, "Minimum Passing", False, False),
        (5.0, 40.0, "Failing", False, False),
    ]
    
    print("\n📊 OFFICIAL GRADE POINTS:")
    print("-" * 80)
    print(f"{'GWA':<8} {'Percent':<10} {'Description':<20} {'Basic':<10} {'Merit':<10}")
    print("-" * 80)
    
    # Create a test instance for conversion
    test_submission = GradeSubmission(
        general_weighted_average=Decimal('1.0'),
        total_units=20
    )
    
    all_passed = True
    for gwa, expected_percent, description, should_qualify_basic, should_qualify_merit in test_cases:
        # Test conversion
        test_submission.general_weighted_average = Decimal(str(gwa))
        actual_percent = test_submission._convert_to_percentage(float(gwa))
        
        # Check merit (GWA <= 1.75, which is >= 88%)
        qualifies_merit = actual_percent >= 88.0
        
        # Check basic (GWA <= 2.25, which is >= 80%)
        qualifies_basic = actual_percent >= 80.0
        
        # Verify expectations
        percent_match = abs(actual_percent - expected_percent) < 0.1
        basic_match = qualifies_basic == should_qualify_basic
        merit_match = qualifies_merit == should_qualify_merit
        
        status = "✅" if (percent_match and basic_match and merit_match) else "❌"
        if not (percent_match and basic_match and merit_match):
            all_passed = False
        
        basic_icon = "✓" if qualifies_basic else "✗"
        merit_icon = "✓" if qualifies_merit else "✗"
        
        print(f"{status} {gwa:<6} {actual_percent:<8.2f}% {description:<20} {basic_icon:<10} {merit_icon:<10}")
    
    print("-" * 80)
    
    # Test flexible decimal formats
    print("\n🔢 FLEXIBLE DECIMAL FORMAT TEST:")
    print("-" * 80)
    flexible_formats = [
        (1, 98.0),
        (1.0, 98.0),
        (1.75, 88.0),
        (1.7, 86.8),  # Interpolated
        (1.8, 89.2),  # Interpolated
        (1.91, 86.56),  # Interpolated
        (2, 85.0),
        (2.0, 85.0),
        (2.25, 82.0),
    ]
    
    print(f"{'Input':<10} {'Converted':<12} {'Expected':<12} {'Status':<10}")
    print("-" * 80)
    
    for input_val, expected in flexible_formats:
        test_submission.general_weighted_average = Decimal(str(input_val))
        result = test_submission._convert_to_percentage(float(input_val))
        
        # Allow small tolerance for interpolated values
        match = abs(result - expected) < 0.5
        status = "✅" if match else "❌"
        if not match:
            all_passed = False
        
        print(f"{status} {input_val:<8} {result:<10.2f}% {expected:<10.2f}%")
    
    print("-" * 80)
    
    # Test eligibility thresholds
    print("\n🎯 ELIGIBILITY THRESHOLD TEST:")
    print("-" * 80)
    print(f"{'GWA':<10} {'Percent':<12} {'Basic':<15} {'Merit':<15}")
    print("-" * 80)
    
    threshold_tests = [
        (1.74, "Should get Merit"),
        (1.75, "Should get Merit (cutoff)"),
        (1.76, "Should get Basic only"),
        (2.24, "Should get Basic only"),
        (2.25, "Should get Basic (cutoff)"),
        (2.26, "Should get None"),
    ]
    
    for gwa, note in threshold_tests:
        test_submission.general_weighted_average = Decimal(str(gwa))
        percent = test_submission._convert_to_percentage(float(gwa))
        
        qualifies_basic = percent >= 80.0
        qualifies_merit = percent >= 88.0
        
        basic_status = "✅ Yes" if qualifies_basic else "❌ No"
        merit_status = "✅ Yes" if qualifies_merit else "❌ No"
        
        print(f"{gwa:<8.2f} {percent:<10.2f}% {basic_status:<15} {merit_status:<15} ({note})")
    
    print("-" * 80)
    
    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED! New grading scale is working correctly!")
    else:
        print("❌ SOME TESTS FAILED! Please review the conversion function.")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_grading_scale()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
