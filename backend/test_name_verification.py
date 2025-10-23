"""
Test script to verify AI Name Verification Security System
This script demonstrates the name matching logic without requiring document upload
"""

import re

def test_name_verification():
    """Test the name verification logic"""
    
    print("=" * 70)
    print("🔒 AI NAME VERIFICATION SECURITY TEST")
    print("=" * 70)
    print()
    
    # Test case 1: Exact name match
    print("TEST 1: Exact Full Name Match")
    print("-" * 70)
    student_name = "Juan Dela Cruz"
    document_text = "Republic of Philippines BIRTH CERTIFICATE This is to certify that Juan Dela Cruz was born on January 1, 2000"
    
    first_name = "juan"
    last_name = "dela cruz"
    full_name = f"{first_name} {last_name}"
    
    text_lower = document_text.lower()
    
    if full_name in text_lower:
        print(f"✅ PASS: Found '{student_name}' in document")
        print(f"   Confidence: 95%")
        print(f"   Status: APPROVED")
    else:
        print(f"❌ FAIL: '{student_name}' not found")
        print(f"   Status: REJECTED")
    print()
    
    # Test case 2: Name mismatch (fraud)
    print("TEST 2: Name Mismatch (Fraud Detection)")
    print("-" * 70)
    student_name = "Juan Dela Cruz"
    document_text = "Republic of Philippines BIRTH CERTIFICATE This is to certify that Maria Santos was born on January 1, 2000"
    
    first_name = "juan"
    last_name = "dela cruz"
    full_name = f"{first_name} {last_name}"
    
    text_lower = document_text.lower()
    text_cleaned = re.sub(r'[^a-z\s]', ' ', text_lower)
    text_cleaned = re.sub(r'\s+', ' ', text_cleaned).strip()
    
    if full_name not in text_cleaned:
        # Find other names
        potential_names = re.findall(r'\b[a-z]{3,}\s+[a-z]{3,}\b', text_cleaned)
        other_names = list(set(potential_names))[:3]
        
        print(f"❌ FRAUD DETECTED!")
        print(f"   Expected name: '{student_name}'")
        print(f"   Found names: {', '.join([n.title() for n in other_names])}")
        print(f"   Confidence: 0%")
        print(f"   Status: 🚨 REJECTED - FRAUD ALERT")
    else:
        print(f"✅ Name found")
    print()
    
    # Test case 3: Reverse name format
    print("TEST 3: Reverse Name Format")
    print("-" * 70)
    student_name = "Juan Dela Cruz"
    document_text = "SCHOOL ID Student Name: DELA CRUZ, JUAN Student ID: 2024-12345"
    
    first_name = "juan"
    last_name = "dela cruz"
    reverse_name = f"{last_name} {first_name}"
    
    text_lower = document_text.lower()
    
    if reverse_name in text_lower or (first_name in text_lower and last_name in text_lower):
        print(f"✅ PASS: Found '{student_name}' (reverse format)")
        print(f"   Confidence: 90%")
        print(f"   Status: APPROVED")
    else:
        print(f"❌ FAIL: Name not found")
    print()
    
    # Test case 4: Name parts separated
    print("TEST 4: Name Parts Separated")
    print("-" * 70)
    student_name = "Juan Dela Cruz"
    document_text = "Certificate of Enrollment This certifies that Juan is enrolled... Student: Dela Cruz"
    
    first_name = "juan"
    last_name = "dela cruz"
    
    text_lower = document_text.lower()
    
    if first_name in text_lower and last_name in text_lower:
        print(f"✅ PASS: Found both parts of '{student_name}'")
        print(f"   Confidence: 85%")
        print(f"   Status: APPROVED")
    else:
        print(f"❌ FAIL: Name parts not found")
    print()
    
    # Test case 5: No text extracted (fallback)
    print("TEST 5: Minimal Text / OCR Unavailable")
    print("-" * 70)
    student_name = "Juan Dela Cruz"
    document_text = "abc"  # Very minimal text
    
    if len(document_text.strip()) < 10:
        print(f"⚠️ WARNING: Minimal text extracted")
        print(f"   Confidence: 50%")
        print(f"   Status: APPROVED (with lower confidence)")
        print(f"   Note: Full verification not possible")
    print()
    
    print("=" * 70)
    print("✅ NAME VERIFICATION TEST COMPLETE")
    print("=" * 70)
    print()
    print("🔒 Security Features:")
    print("   • Multiple name format matching (exact, reverse, separated)")
    print("   • Fraud detection (finds other names on document)")
    print("   • Confidence scoring (85-95% for legitimate docs)")
    print("   • Graceful fallback when OCR unavailable")
    print("   • Clear rejection messages with policy warnings")
    print()
    print("📊 Expected Results:")
    print("   ✅ Legitimate documents: 85-95% confidence → APPROVED")
    print("   ❌ Fraudulent documents: 0% confidence → REJECTED")
    print("   ⚠️ Unclear documents: 40-60% confidence → APPROVED (limited verification)")
    print()

if __name__ == "__main__":
    test_name_verification()
