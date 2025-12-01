"""
🤖 Create Sample AI-Processed Documents
Generates realistic sample documents with AI analysis results for testing and demonstration
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from myapp.models import DocumentSubmission
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

def create_sample_ai_documents():
    """Create sample documents with AI processing results"""
    
    print("🤖 Creating Sample AI-Processed Documents")
    print("=" * 60)
    
    # Get or create a test user
    try:
        user = User.objects.filter(is_staff=False, role='student').first()
        if not user:
            print("Creating test student user...")
            user = User.objects.create_user(
                username='test_student',
                email='test@student.tcu.edu.ph',
                password='testpass123',
                first_name='Test',
                last_name='Student',
                role='student',
                student_id='24-00001',
                is_staff=False,
                is_superuser=False,
                is_email_verified=True
            )
        print(f"✅ Using student: {user.username} ({user.first_name} {user.last_name})")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Define sample documents with AI results
    sample_documents = [
        {
            'document_type': 'birth_certificate',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.95,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Document validated successfully. All 6 AI algorithms passed with high confidence.',
            'ai_key_information': {
                'document_validator': {'confidence': 0.93, 'status': 'passed'},
                'face_verifier': {'confidence': 0.88, 'status': 'passed'},
                'fraud_detector': {'confidence': 0.97, 'fraud_probability': 0.03}
            },
            'ai_recommendations': ['Document is authentic', 'High quality scan', 'Auto-approved by AI'],
            'ai_extracted_text': 'REPUBLIC OF THE PHILIPPINES\nOFFICE OF THE CIVIL REGISTRAR\nCERTIFICATE OF LIVE BIRTH'
        },
        {
            'document_type': 'grade_12_report_card',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.89,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Grade verification completed. GWA calculation validated.',
            'ai_key_information': {
                'grade_verifier': {'confidence': 0.91, 'gwa': 92.5, 'status': 'eligible'},
                'document_validator': {'confidence': 0.87, 'status': 'passed'},
                'fraud_detector': {'confidence': 0.89, 'fraud_probability': 0.11}
            },
            'ai_recommendations': ['Grades verified successfully', 'Eligible for allowance', 'High academic performance'],
            'ai_extracted_text': 'GRADE 12 REPORT CARD\nStudent Name: Test Student\nGeneral Weighted Average: 92.5'
        },
        {
            'document_type': 'barangay_certificate',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.92,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Document authenticated. All verification checks passed.',
            'ai_key_information': {
                'document_validator': {'confidence': 0.94, 'status': 'passed'},
                'cross_document_matcher': {'confidence': 0.90, 'name_match': True},
                'fraud_detector': {'confidence': 0.92, 'fraud_probability': 0.08}
            },
            'ai_recommendations': ['Document authentic', 'Name matches other documents', 'Auto-approved'],
            'ai_extracted_text': 'BARANGAY CERTIFICATE\nThis is to certify that...'
        },
        {
            'document_type': 'proof_of_enrollment',
            'status': 'manual_review',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.67,
            'ai_auto_approved': False,
            'ai_analysis_notes': 'Medium confidence. Some quality issues detected. Manual review recommended.',
            'ai_key_information': {
                'document_validator': {'confidence': 0.65, 'status': 'passed'},
                'fraud_detector': {'confidence': 0.72, 'fraud_probability': 0.28},
                'quality_assessment': {'score': 0.64, 'issues': ['Low resolution', 'Partial blur']}
            },
            'ai_recommendations': ['Manual review required', 'Check document quality', 'Verify enrollment details'],
            'ai_extracted_text': 'CERTIFICATE OF ENROLLMENT\nSchool Year 2023-2024'
        },
        {
            'document_type': 'id_picture',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.88,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Face verification successful. Image quality acceptable.',
            'ai_key_information': {
                'face_verifier': {'confidence': 0.91, 'faces_detected': 1, 'status': 'passed'},
                'document_validator': {'confidence': 0.85, 'status': 'passed'},
                'quality_assessment': {'score': 0.88, 'resolution': 'good'}
            },
            'ai_recommendations': ['Face detected successfully', 'Image quality good', 'Auto-approved'],
            'ai_extracted_text': 'ID Picture - Student Photo'
        },
        {
            'document_type': 'parent_id',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.86,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Parent ID validated successfully with face detection.',
            'ai_key_information': {
                'document_validator': {'confidence': 0.84, 'status': 'passed'},
                'face_verifier': {'confidence': 0.89, 'faces_detected': 1, 'status': 'passed'},
                'fraud_detector': {'confidence': 0.85, 'fraud_probability': 0.15}
            },
            'ai_recommendations': ['Valid ID document', 'Face detected', 'Auto-approved'],
            'ai_extracted_text': 'VALID ID\nDEPARTMENT OF...'
        },
        {
            'document_type': 'grade_10_report_card',
            'status': 'manual_review',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.71,
            'ai_auto_approved': False,
            'ai_analysis_notes': 'Grade extraction completed but requires verification due to OCR uncertainties.',
            'ai_key_information': {
                'grade_verifier': {'confidence': 0.69, 'gwa': 85.2, 'status': 'uncertain'},
                'document_validator': {'confidence': 0.73, 'status': 'passed'},
                'ocr_quality': {'score': 0.68, 'issues': ['Handwritten grades', 'OCR uncertain']}
            },
            'ai_recommendations': ['Verify extracted grades manually', 'Check GWA calculation', 'OCR confidence medium'],
            'ai_extracted_text': 'GRADE 10 REPORT CARD\nGeneral Average: 85.2'
        },
        {
            'document_type': 'income_certificate',
            'status': 'approved',
            'ai_analysis_completed': True,
            'ai_confidence_score': 0.90,
            'ai_auto_approved': True,
            'ai_analysis_notes': 'Income certificate validated. All checks passed.',
            'ai_key_information': {
                'document_validator': {'confidence': 0.91, 'status': 'passed'},
                'fraud_detector': {'confidence': 0.89, 'fraud_probability': 0.11},
                'cross_document_matcher': {'confidence': 0.90, 'family_name_match': True}
            },
            'ai_recommendations': ['Document authentic', 'Income verified', 'Auto-approved'],
            'ai_extracted_text': 'CERTIFICATE OF INCOME\nThis is to certify that...'
        }
    ]
    
    created_count = 0
    
    # Create documents with staggered timestamps
    for i, doc_data in enumerate(sample_documents):
        try:
            # Create document with timestamp in the past 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            submitted_time = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            document = DocumentSubmission.objects.create(
                student=user,
                document_type=doc_data['document_type'],
                status=doc_data['status'],
                submitted_at=submitted_time,
                ai_analysis_completed=doc_data['ai_analysis_completed'],
                ai_confidence_score=doc_data['ai_confidence_score'],
                ai_auto_approved=doc_data['ai_auto_approved'],
                ai_analysis_notes=doc_data['ai_analysis_notes'],
                ai_key_information=doc_data['ai_key_information'],
                ai_recommendations=doc_data['ai_recommendations'],
                ai_extracted_text=doc_data['ai_extracted_text'],
                reviewed_at=submitted_time + timedelta(minutes=random.randint(1, 30))
            )
            
            created_count += 1
            status_icon = '✅' if doc_data['status'] == 'approved' else '👁️'
            print(f"{status_icon} Created: {doc_data['document_type']} (Confidence: {doc_data['ai_confidence_score']:.2f})")
            
        except Exception as e:
            print(f"❌ Error creating {doc_data['document_type']}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Created {created_count} sample AI-processed documents!")
    
    # Display statistics
    total = DocumentSubmission.objects.count()
    ai_processed = DocumentSubmission.objects.filter(ai_analysis_completed=True).count()
    auto_approved = DocumentSubmission.objects.filter(ai_auto_approved=True).count()
    
    print(f"\n📊 Current Database Statistics:")
    print(f"   Total Documents: {total}")
    print(f"   AI Processed: {ai_processed}")
    print(f"   Auto Approved: {auto_approved}")
    print(f"   Auto Approval Rate: {(auto_approved/ai_processed*100):.1f}%")
    
    # Calculate average confidence
    from django.db.models import Avg
    avg_confidence = DocumentSubmission.objects.filter(
        ai_analysis_completed=True
    ).aggregate(avg=Avg('ai_confidence_score'))['avg']
    
    print(f"   Average Confidence: {avg_confidence:.3f} ({avg_confidence*100:.1f}%)")
    
    print(f"\n🎉 AI Dashboard should now display meaningful data!")
    print(f"   Navigate to Admin Dashboard > AI System tab to view results.")

if __name__ == '__main__':
    try:
        create_sample_ai_documents()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
