"""
Test file upload validators
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.validators import (
    FileSizeValidator, 
    FileTypeValidator, 
    MaliciousFileValidator,
    ProfileImageValidator
)
from django.core.exceptions import ValidationError

def test_file_size_validator():
    print("\n" + "="*60)
    print("TESTING FILE SIZE VALIDATOR")
    print("="*60)
    
    validator = FileSizeValidator(max_size_mb=10, min_size_kb=1)
    
    # Test 1: File too large
    print("\n1. Testing file too large (15MB):")
    large_file = SimpleUploadedFile("test.pdf", b"x" * (15 * 1024 * 1024))
    try:
        validator(large_file)
        print("   ✗ FAILED: Should have rejected large file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    # Test 2: File too small
    print("\n2. Testing file too small (500 bytes):")
    tiny_file = SimpleUploadedFile("test.pdf", b"x" * 500)
    try:
        validator(tiny_file)
        print("   ✗ FAILED: Should have rejected tiny file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    # Test 3: Valid file size
    print("\n3. Testing valid file size (5MB):")
    valid_file = SimpleUploadedFile("test.pdf", b"x" * (5 * 1024 * 1024))
    try:
        validator(valid_file)
        print("   ✓ PASSED: File accepted")
    except ValidationError as e:
        print(f"   ✗ FAILED: {e.message}")

def test_file_type_validator():
    print("\n" + "="*60)
    print("TESTING FILE TYPE VALIDATOR")
    print("="*60)
    
    validator = FileTypeValidator(allowed_category='document')
    
    # Test 1: Valid PDF
    print("\n1. Testing valid PDF:")
    pdf_file = SimpleUploadedFile("test.pdf", b"content", content_type='application/pdf')
    try:
        validator(pdf_file)
        print("   ✓ PASSED: PDF accepted")
    except ValidationError as e:
        print(f"   ✗ FAILED: {e.message}")
    
    # Test 2: Invalid file type
    print("\n2. Testing invalid file type (executable):")
    exe_file = SimpleUploadedFile("test.exe", b"content", content_type='application/x-msdownload')
    try:
        validator(exe_file)
        print("   ✗ FAILED: Should have rejected executable")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    # Test 3: Extension mismatch
    print("\n3. Testing extension mismatch (.jpg file with .pdf extension):")
    mismatch_file = SimpleUploadedFile("test.pdf", b"content", content_type='image/jpeg')
    try:
        validator(mismatch_file)
        print("   ✗ FAILED: Should have rejected mismatched file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")

def test_malicious_file_validator():
    print("\n" + "="*60)
    print("TESTING MALICIOUS FILE VALIDATOR")
    print("="*60)
    
    validator = MaliciousFileValidator()
    
    # Test 1: Executable disguised as PDF
    print("\n1. Testing executable disguised as PDF:")
    exe_content = b"MZ\x90\x00" + b"x" * 1000  # Windows executable signature
    fake_pdf = SimpleUploadedFile("document.pdf", exe_content, content_type='application/pdf')
    try:
        validator(fake_pdf)
        print("   ✗ FAILED: Should have detected malicious file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    # Test 2: Script injection attempt
    print("\n2. Testing script injection:")
    script_content = b"<script>alert('xss')</script>" + b"x" * 1000
    fake_doc = SimpleUploadedFile("document.pdf", script_content, content_type='application/pdf')
    try:
        validator(fake_doc)
        print("   ✗ FAILED: Should have detected script content")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    # Test 3: Valid file
    print("\n3. Testing valid file:")
    valid_content = b"This is a normal document content"
    valid_file = SimpleUploadedFile("document.pdf", valid_content, content_type='application/pdf')
    try:
        validator(valid_file)
        print("   ✓ PASSED: Valid file accepted")
    except ValidationError as e:
        print(f"   ✗ FAILED: {e.message}")
    
    # Test 4: Dangerous extension
    print("\n4. Testing dangerous extension (.exe):")
    exe_file = SimpleUploadedFile("virus.exe", b"content", content_type='application/x-msdownload')
    try:
        validator(exe_file)
        print("   ✗ FAILED: Should have rejected .exe file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")

def test_comprehensive_validation():
    print("\n" + "="*60)
    print("TESTING COMPREHENSIVE VALIDATION CHAIN")
    print("="*60)
    
    # Simulate what happens during actual upload
    from myapp.validators import document_validators
    
    print("\n1. Testing valid document (PDF, 2MB):")
    valid_doc = SimpleUploadedFile(
        "transcript.pdf", 
        b"Valid PDF content" * 100000,  # ~2MB
        content_type='application/pdf'
    )
    try:
        for validator in document_validators:
            validator(valid_doc)
            valid_doc.seek(0)  # Reset file pointer for next validator
        print("   ✓ PASSED: All validators passed")
    except ValidationError as e:
        print(f"   ✗ FAILED: {e.message}")
    
    print("\n2. Testing invalid document (too large, 15MB):")
    large_doc = SimpleUploadedFile(
        "large.pdf", 
        b"x" * (15 * 1024 * 1024),
        content_type='application/pdf'
    )
    try:
        for validator in document_validators:
            validator(large_doc)
            large_doc.seek(0)
        print("   ✗ FAILED: Should have rejected large file")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")
    
    print("\n3. Testing malicious file (executable disguised as PDF):")
    malicious_doc = SimpleUploadedFile(
        "fake.pdf", 
        b"MZ\x90\x00" + b"x" * 10000,
        content_type='application/pdf'
    )
    try:
        for validator in document_validators:
            validator(malicious_doc)
            malicious_doc.seek(0)
        print("   ✗ FAILED: Should have detected malicious content")
    except ValidationError as e:
        print(f"   ✓ PASSED: {e.message}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("FILE UPLOAD VALIDATOR TESTS")
    print("="*60)
    
    test_file_size_validator()
    test_file_type_validator()
    test_malicious_file_validator()
    test_comprehensive_validation()
    
    print("\n" + "="*60)
    print("✅ ALL VALIDATOR TESTS COMPLETE")
    print("="*60)
