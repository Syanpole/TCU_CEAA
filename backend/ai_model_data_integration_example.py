"""
🔗 AI Model Data Integration Example
Shows how to integrate the model data loader with existing AI verification algorithms
"""

from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from ai_verification.model_data_loader import AIModelDataLoader, DocumentTemplateValidator
from ai_verification.advanced_algorithms import DocumentValidator

class EnhancedDocumentValidator(DocumentValidator):
    """
    Enhanced Document Validator that uses reference documents and templates
    """
    
    def __init__(self):
        super().__init__()
        self.model_loader = AIModelDataLoader()
        self.template_validator = DocumentTemplateValidator(self.model_loader)
        
    def validate_with_template(self, document_path: str, document_type: str) -> dict:
        """
        Validate document using both OCR and template matching
        """
        result = {
            'document_path': document_path,
            'document_type': document_type,
            'template_validation': {},
            'reference_comparison': {},
            'overall_confidence': 0.0,
            'is_valid': False
        }
        
        try:
            # Get document template
            template = self.model_loader.get_document_template(document_type)
            if not template:
                result['error'] = f"No template found for document type: {document_type}"
                return result
            
            # Extract text using existing OCR functionality
            extracted_text = self._extract_text_from_document(document_path)
            
            # Validate against template
            template_result = self.template_validator.validate_document_structure(
                document_type, extracted_text
            )
            result['template_validation'] = template_result
            
            # Get reference documents for comparison
            reference_docs = self.model_loader.get_reference_documents(document_type)
            if reference_docs:
                result['reference_comparison'] = {
                    'available_references': len(reference_docs),
                    'reference_files': [str(ref.name) for ref in reference_docs[:3]]  # Show first 3
                }
            
            # Calculate overall confidence
            template_confidence = template_result.get('confidence', 0.0)
            structure_confidence = 0.8 if template_result.get('valid', False) else 0.3
            
            result['overall_confidence'] = (template_confidence * 0.7 + structure_confidence * 0.3)
            result['is_valid'] = result['overall_confidence'] >= self.model_loader.get_confidence_threshold(document_type)
            
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _extract_text_from_document(self, document_path: str) -> str:
        """
        Extract text from document (placeholder - use existing OCR functionality)
        """
        # This would use your existing OCR extraction logic
        # For demo purposes, return sample text
        return """
        REPUBLIC OF THE PHILIPPINES
        PHILIPPINE STATISTICS AUTHORITY
        CIVIL REGISTRATION
        
        CERTIFICATE OF LIVE BIRTH
        
        NAME: JUAN DELA CRUZ
        DATE OF BIRTH: JANUARY 1, 2000
        PLACE OF BIRTH: MANILA, PHILIPPINES
        FATHER: JOSE DELA CRUZ
        MOTHER: MARIA SANTOS
        """


def demo_template_validation():
    """Demonstrate template-based validation"""
    print("🔍 AI Model Data Integration Demo")
    print("=" * 50)
    
    # Initialize enhanced validator
    validator = EnhancedDocumentValidator()
    
    # Test different document types
    test_cases = [
        ('birth_certificate', 'Sample birth certificate validation'),
        ('school_id', 'Sample school ID validation'),
        ('report_card', 'Sample report card validation')
    ]
    
    for doc_type, description in test_cases:
        print(f"\n📄 Testing {description}...")
        
        # Simulate document validation
        result = validator.validate_with_template(
            f"sample_{doc_type}.pdf", 
            doc_type
        )
        
        print(f"   Document Type: {result['document_type']}")
        print(f"   Template Valid: {result['template_validation'].get('valid', False)}")
        print(f"   Template Confidence: {result['template_validation'].get('confidence', 0.0):.2f}")
        print(f"   Missing Fields: {len(result['template_validation'].get('missing_fields', []))}")
        print(f"   Overall Confidence: {result['overall_confidence']:.2f}")
        print(f"   Is Valid: {'✅' if result['is_valid'] else '❌'}")
        
        # Show reference comparison info
        ref_info = result.get('reference_comparison', {})
        if ref_info:
            print(f"   Reference Docs: {ref_info.get('available_references', 0)} available")


if __name__ == "__main__":
    demo_template_validation()