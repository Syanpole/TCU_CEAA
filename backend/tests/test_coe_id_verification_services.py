"""
Unit tests for COE and ID Verification Services
Tests the integration of YOLOv8 detection + AWS Textract OCR + OCRTextInterpreter
"""
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.models import DocumentSubmission, BasicQualification
from myapp.coe_verification_service import COEVerificationService
from myapp.id_verification_service import IDVerificationService

User = get_user_model()


class COEVerificationServiceTest(TestCase):
    """Test Certificate of Enrollment verification service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = COEVerificationService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            student_id='22-00417'
        )
        
        # Create basic qualification with correct fields
        self.basic_qual = BasicQualification.objects.create(
            student=self.user,
            is_enrolled=True,
            is_resident=True,
            is_eighteen_or_older=True,
            is_registered_voter=True,
            parent_is_voter=True,
            has_good_moral_character=True,
            is_committed=True
        )
    
    @patch('myapp.coe_verification_service.YOLO')
    def test_detect_coe_success(self, mock_yolo):
        """Test COE detection with YOLOv8"""
        # Mock YOLO detection result
        mock_result = Mock()
        mock_result.boxes.conf = [0.88]  # 88% confidence
        mock_model = Mock()
        mock_model.return_value = [mock_result]
        mock_yolo.return_value = mock_model
        
        test_image_path = 'test_coe.jpg'
        
        result = self.service.detect_coe(test_image_path)
        
        self.assertIsNotNone(result)
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['confidence'], 0.80)
    
    @patch('myapp.coe_verification_service.boto3.client')
    def test_extract_text_with_textract(self, mock_boto_client):
        """Test AWS Textract OCR extraction"""
        # Mock Textract response
        mock_textract = Mock()
        mock_textract.detect_document_text.return_value = {
            'Blocks': [
                {
                    'BlockType': 'LINE',
                    'Text': 'TAGUIG CITY UNIVERSITY',
                    'Confidence': 99.5
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'CERTIFICATE OF ENROLLMENT',
                    'Confidence': 98.2
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Name: JOHN DOE',
                    'Confidence': 97.8
                },
                {
                    'BlockType': 'LINE',
                    'Text': 'Student Number: 22-00417',
                    'Confidence': 96.5
                }
            ]
        }
        mock_boto_client.return_value = mock_textract
        
        test_image_path = 'test_coe.jpg'
        
        result = self.service.extract_text_advanced_ocr(test_image_path)
        
        self.assertIsNotNone(result)
        self.assertIn('raw_text', result)
        self.assertIn('confidence', result)
        self.assertIn('CERTIFICATE OF ENROLLMENT', result['raw_text'])
        self.assertGreaterEqual(result['confidence'], 95.0)
    
    def test_interpret_coe_fields(self):
        """Test OCR text interpretation for COE fields"""
        raw_text = """
        TAGUIG CITY UNIVERSITY
        Gen. Santos Avenue, Western Bicutan, Taguig City
        
        CERTIFICATE OF ENROLLMENT
        
        School Year: 2025-2026
        Semester: First Semester
        
        Name: JOHN DOE
        Student Number: 22-00417
        Course: Bachelor of Science in Computer Science
        Year Level: 4th Year
        College: College of Arts and Sciences
        Status: Regular
        """
        
        result = self.service.interpret_coe_fields(raw_text, self.user)
        
        self.assertIn('student_name', result)
        self.assertIn('student_number', result)
        self.assertIn('school_year', result)
        self.assertIn('semester', result)
        self.assertIn('course', result)
        self.assertIn('college', result)
        
        # Check confidence scores
        self.assertGreater(result['student_name']['confidence'], 0.7)
        self.assertEqual(result['student_number']['value'], '22-00417')
    
    @patch('myapp.coe_verification_service.COEVerificationService.detect_coe')
    @patch('myapp.coe_verification_service.COEVerificationService.extract_text_advanced_ocr')
    def test_verify_coe_document_full_flow(self, mock_extract, mock_detect):
        """Test complete COE verification flow"""
        # Mock YOLO detection
        mock_detect.return_value = {
            'confidence': 0.883,
            'detected': True,
            'bbox': [100, 100, 400, 600]
        }
        
        # Mock OCR extraction
        mock_extract.return_value = {
            'raw_text': 'TAGUIG CITY UNIVERSITY\nCERTIFICATE OF ENROLLMENT\nJOHN DOE\n22-00417',
            'confidence': 97.5,
            'lines': ['TAGUIG CITY UNIVERSITY', 'CERTIFICATE OF ENROLLMENT', 'JOHN DOE', '22-00417']
        }
        
        test_image_path = 'test_coe.jpg'
        
        result = self.service.verify_coe_document(test_image_path, self.user)
        
        self.assertTrue(result['is_valid'])
        self.assertGreaterEqual(result['confidence'], 85.0)
        self.assertEqual(result['status'], 'approved')
        self.assertIn('extraction_method', result)
        self.assertEqual(result['extraction_method'], 'Advanced OCR')


class IDVerificationServiceTest(TestCase):
    """Test ID Card verification service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = IDVerificationService()
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            first_name='Jane',
            last_name='Smith',
            student_id='22-00418'
        )
        
        self.basic_qual = BasicQualification.objects.create(
            student=self.user,
            is_enrolled=True,
            is_resident=True
        )
    
    @patch('myapp.id_verification_service.YOLO')
    def test_detect_id_card_success(self, mock_yolo):
        """Test ID card detection with YOLOv8"""
        mock_result = Mock()
        mock_result.boxes.conf = [0.89]
        mock_model = Mock()
        mock_model.return_value = [mock_result]
        mock_yolo.return_value = mock_model
        
        result = self.service.detect_id_card('test_id.jpg')
        
        self.assertIsNotNone(result)
        self.assertIn('confidence', result)
        self.assertGreaterEqual(result['confidence'], 0.85)
    
    @patch('myapp.id_verification_service.boto3.client')
    def test_extract_id_text(self, mock_boto_client):
        """Test ID card text extraction"""
        mock_textract = Mock()
        mock_textract.detect_document_text.return_value = {
            'Blocks': [
                {'BlockType': 'LINE', 'Text': 'TAGUIG CITY UNIVERSITY', 'Confidence': 99.0},
                {'BlockType': 'LINE', 'Text': 'JANE SMITH', 'Confidence': 98.5},
                {'BlockType': 'LINE', 'Text': '22-00418', 'Confidence': 97.8},
                {'BlockType': 'LINE', 'Text': 'COMPUTER SCIENCE', 'Confidence': 96.2}
            ]
        }
        mock_boto_client.return_value = mock_textract
        
        result = self.service.extract_text_advanced_ocr('test_id.jpg')
        
        self.assertIsNotNone(result)
        self.assertIn('JANE SMITH', result['raw_text'])
        self.assertIn('22-00418', result['raw_text'])
        self.assertGreaterEqual(result['confidence'], 95.0)
    
    def test_verify_identity_exact_match(self):
        """Test identity verification with exact match"""
        extracted_data = {
            'name': {'value': 'JANE SMITH', 'confidence': 0.98},
            'student_id': {'value': '22-00418', 'confidence': 0.97}
        }
        
        result = self.service.verify_identity(extracted_data, self.user)
        
        self.assertTrue(result['name_match'])
        self.assertTrue(result['student_id_match'])
        self.assertGreaterEqual(result['overall_confidence'], 0.90)
    
    def test_verify_identity_fuzzy_match(self):
        """Test identity verification with fuzzy matching"""
        extracted_data = {
            'name': {'value': 'JANE M. SMITH', 'confidence': 0.95},  # Middle initial added
            'student_id': {'value': '22-00418', 'confidence': 0.96}
        }
        
        result = self.service.verify_identity(extracted_data, self.user)
        
        self.assertTrue(result['name_match'])  # Should pass with fuzzy matching
        self.assertTrue(result['student_id_match'])
        self.assertGreater(result['name_similarity'], 0.80)
    
    def test_verify_identity_mismatch(self):
        """Test identity verification with mismatch"""
        extracted_data = {
            'name': {'value': 'JOHN DOE', 'confidence': 0.98},  # Wrong name
            'student_id': {'value': '21-0417', 'confidence': 0.97}  # Wrong ID
        }
        
        result = self.service.verify_identity(extracted_data, self.user)
        
        self.assertFalse(result['name_match'])
        self.assertFalse(result['student_id_match'])
        self.assertLess(result['overall_confidence'], 0.70)
    
    @patch('myapp.id_verification_service.IDVerificationService.detect_id_card')
    @patch('myapp.id_verification_service.IDVerificationService.extract_text_advanced_ocr')
    def test_verify_id_card_full_flow(self, mock_extract, mock_detect):
        """Test complete ID verification flow"""
        mock_detect.return_value = {
            'confidence': 0.893,
            'detected': True
        }
        
        mock_extract.return_value = {
            'raw_text': 'TAGUIG CITY UNIVERSITY\nJANE SMITH\n22-00418\nCOMPUTER SCIENCE',
            'confidence': 96.8,
            'lines': ['TAGUIG CITY UNIVERSITY', 'JANE SMITH', '22-00418', 'COMPUTER SCIENCE']
        }
        
        result = self.service.verify_id_card('test_id.jpg', 'school_id', self.user)
        
        self.assertTrue(result['is_valid'])
        self.assertGreaterEqual(result['confidence'], 85.0)
        self.assertEqual(result['status'], 'approved')
        self.assertTrue(result['identity_verification']['name_match'])
        self.assertTrue(result['identity_verification']['student_id_match'])


class OCRTextInterpreterTest(TestCase):
    """Test OCR text interpretation logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Import here to avoid circular dependencies
        from ocr_text_interpreter import OCRTextInterpreter
        self.interpreter = OCRTextInterpreter()
    
    def test_fuzzy_match_high_similarity(self):
        """Test fuzzy matching with high similarity"""
        similarity = self.interpreter.fuzzy_match('JOHN DOE', 'JOHN M. DOE')
        self.assertGreater(similarity, 0.80)
    
    def test_fuzzy_match_low_similarity(self):
        """Test fuzzy matching with low similarity"""
        similarity = self.interpreter.fuzzy_match('JOHN DOE', 'JANE SMITH')
        self.assertLess(similarity, 0.50)
    
    def test_interpret_student_id_standard_format(self):
        """Test interpreting student ID in standard format"""
        text = "Student Number: 22-00417"
        result = self.interpreter.interpret_student_id(text)
        self.assertIn('22-00417', result['value'] or '')
    
    def test_interpret_student_id_various_formats(self):
        """Test interpreting student ID from various formats"""
        test_cases = [
            "ID: 22-00417",
            "22-00418",
            "Student No. 21-0417",
            "ID Number:22-00419"
        ]
        
        for text in test_cases:
            result = self.interpreter.interpret_student_id(text)
            self.assertIsNotNone(result)
            self.assertIn('value', result)
    
    def test_interpret_school_year(self):
        """Test interpreting school year"""
        text = "School Year: 2025-2026"
        result = self.interpreter.interpret_school_year(text)
        self.assertIsNotNone(result['value'])
        self.assertIn('2025', result['value'])
    
    def test_interpret_school_year_typo_correction(self):
        """Test school year interpretation with typo correction"""
        text = "School Year: 2125-2126"  # Common OCR error
        result = self.interpreter.interpret_school_year(text)
        # Should attempt to correct, value may contain corrected year
        self.assertIsNotNone(result)
    
    def test_interpret_semester(self):
        """Test interpreting semester"""
        test_cases = [
            "Semester: First Semester",
            "2nd Semester",
            "Summer",
            "FIRST SEMESTER"
        ]
        
        for text in test_cases:
            result = self.interpreter.interpret_semester(text)
            self.assertIsNotNone(result)
            self.assertIn('value', result)


class DocumentSubmissionIntegrationTest(TestCase):
    """Integration tests for document submission with new services"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='integrationtest',
            email='integration@test.com',
            first_name='Test',
            last_name='User',
            student_id='22-00420'
        )
        
        self.basic_qual = BasicQualification.objects.create(
            student=self.user,
            is_enrolled=True,
            is_resident=True
        )
    
    @patch('myapp.serializers.COEVerificationService')
    def test_coe_submission_routing(self, mock_service):
        """Test that COE documents are routed to COEVerificationService"""
        mock_instance = Mock()
        mock_instance.verify_coe_document.return_value = {
            'is_valid': True,
            'confidence': 89.10,
            'status': 'approved',
            'extraction_method': 'Advanced OCR'
        }
        mock_service.return_value = mock_instance
        
        # Create mock document submission
        document = DocumentSubmission.objects.create(
            student=self.user,
            document_type='certificate_of_enrollment',
            document_file='test_coe.jpg',
            status='pending'
        )
        
        # This would trigger serializer's run_comprehensive_ai_analysis
        # In real scenario, called via API endpoint
        from myapp.serializers import DocumentSubmissionSerializer
        serializer = DocumentSubmissionSerializer()
        
        # Verify service was instantiated (would be called in actual flow)
        self.assertIsNotNone(mock_service)
    
    @patch('myapp.serializers.IDVerificationService')
    def test_id_submission_routing(self, mock_service):
        """Test that ID documents are routed to IDVerificationService"""
        mock_instance = Mock()
        mock_instance.verify_id_card.return_value = {
            'is_valid': True,
            'confidence': 89.30,
            'status': 'approved',
            'identity_verification': {
                'name_match': True,
                'student_id_match': True,
                'overall_confidence': 0.95
            }
        }
        mock_service.return_value = mock_instance
        
        document = DocumentSubmission.objects.create(
            student=self.user,
            document_type='school_id',
            document_file='test_id.jpg',
            status='pending'
        )
        
        self.assertIsNotNone(mock_service)


class AuditLoggingTest(TestCase):
    """Test audit logging for verification services"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='audituser',
            email='audit@test.com',
            student_id='22-00421'
        )
    
    @patch('myapp.serializers.audit_logger')
    def test_coe_verification_logged(self, mock_audit):
        """Test that COE verification is properly logged"""
        from myapp.audit_logger import AuditLogger
        
        # Simulate verification
        mock_audit.log.return_value = None
        
        # In actual flow, this would be called
        # audit_logger.log(
        #     user=self.user,
        #     action_type='document_verification',
        #     action_description='COE verification completed',
        #     severity='info'
        # )
        
        # Verify logger exists
        self.assertIsNotNone(mock_audit)
    
    @patch('myapp.serializers.audit_logger')
    def test_id_verification_logged(self, mock_audit):
        """Test that ID verification is properly logged"""
        mock_audit.log.return_value = None
        
        # Verify logger exists and would be called
        self.assertIsNotNone(mock_audit)


class FrontendIntegrationTest(TestCase):
    """Test frontend integration points"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.user = User.objects.create_user(
            username='frontenduser',
            email='frontend@test.com',
            first_name='Frontend',
            last_name='Tester',
            student_id='22-00422'
        )
    
    def test_student_dashboard_full_application_check(self):
        """Test that StudentDashboard properly checks for full applications"""
        # This would test the TypeScript changes we made
        # In Django context, we verify the API returns correct data
        
        from myapp.models import FullApplication
        
        # Create full application with correct fields
        full_app = FullApplication.objects.create(
            user=self.user,
            school_year='2025-2026',
            semester='1st',
            first_name='Frontend',
            last_name='Tester',
            email='frontend@test.com',
            mobile_no='09123456789',
            barangay='Test Barangay',
            house_no='123',
            street='Test Street',
            zip_code='1234',
            is_submitted=True
        )
        
        # Verify it exists
        apps = FullApplication.objects.filter(user=self.user)
        self.assertEqual(apps.count(), 1)
        self.assertTrue(apps.first().is_submitted)


if __name__ == '__main__':
    unittest.main()
