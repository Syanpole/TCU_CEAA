"""
Grades Detection Service
Analyzes grade sheets using OCR and AI to extract grades, calculate GWA,
and determine merit eligibility for scholarship applications.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class GradesDetectionService:
    """Service for detecting and analyzing grades from uploaded documents."""
    
    # Merit level thresholds (GWA scale: 1.00 = highest, 5.00 = fail)
    MERIT_THRESHOLDS = {
        'HIGH_HONORS': 1.50,
        'HONORS': 2.00,
        'MERIT': 2.50,
        'REGULAR': 3.00
    }
    
    def __init__(self):
        """Initialize the grades detection service."""
        self.ocr_service = None  # Will be initialized when needed
    
    def analyze_grade_sheet(self, file_path: str) -> Dict:
        """
        Main method to analyze a grade sheet document.
        
        Args:
            file_path: Path to the grade sheet image/PDF
            
        Returns:
            Dictionary containing:
                - grades_detected: List of detected grades
                - gwa_calculated: Calculated General Weighted Average
                - merit_level: Determined merit classification
                - confidence: Overall confidence score
                - recommendations: List of recommendations
                - raw_text: Extracted text from document
        """
        try:
            # Extract text from grade sheet
            raw_text, confidence = self._extract_text_from_grade_sheet(file_path)
            
            # Extract individual grades
            grades = self._extract_grades(raw_text)
            
            if not grades:
                return {
                    'success': False,
                    'error': 'No grades detected in document',
                    'grades_detected': [],
                    'gwa_calculated': None,
                    'merit_level': None,
                    'confidence': 0,
                    'recommendations': ['Please ensure the document is clear and contains visible grades']
                }
            
            # Calculate GWA
            gwa = self._calculate_gwa(grades)
            
            # Determine merit level
            merit_level = self._determine_merit_level(gwa)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(gwa, merit_level, grades)
            
            return {
                'success': True,
                'grades_detected': grades,
                'gwa_calculated': float(gwa),
                'merit_level': merit_level,
                'confidence': confidence,
                'recommendations': recommendations,
                'raw_text': raw_text[:500],  # Truncate for storage
                'total_subjects': len(grades)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing grade sheet: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'grades_detected': [],
                'gwa_calculated': None,
                'merit_level': None,
                'confidence': 0,
                'recommendations': ['Error processing document. Please try again.']
            }
    
    def _extract_text_from_grade_sheet(self, file_path: str) -> Tuple[str, float]:
        """
        Extract text from grade sheet using OCR.
        
        Args:
            file_path: Path to the grade sheet
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Try AWS Textract first (more accurate)
            try:
                import boto3
                
                textract = boto3.client('textract')
                
                with open(file_path, 'rb') as document:
                    response = textract.detect_document_text(
                        Document={'Bytes': document.read()}
                    )
                
                text_blocks = []
                total_confidence = 0
                count = 0
                
                for block in response.get('Blocks', []):
                    if block['BlockType'] == 'LINE':
                        text_blocks.append(block['Text'])
                        if 'Confidence' in block:
                            total_confidence += block['Confidence']
                            count += 1
                
                text = '\n'.join(text_blocks)
                confidence = (total_confidence / count) / 100 if count > 0 else 0.5
                
                logger.info(f"Textract OCR completed with {confidence:.2%} confidence")
                return text, confidence
                
            except Exception as textract_error:
                logger.warning(f"Textract failed, falling back to Tesseract: {textract_error}")
                
                # Fallback to Tesseract
                try:
                    import pytesseract
                    from PIL import Image
                    
                    # Convert PDF to image if needed
                    if file_path.lower().endswith('.pdf'):
                        from pdf2image import convert_from_path
                        images = convert_from_path(file_path, first_page=1, last_page=1)
                        image = images[0]
                    else:
                        image = Image.open(file_path)
                    
                    # Extract text with confidence
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    
                    text_blocks = []
                    confidences = []
                    
                    for i, conf in enumerate(data['conf']):
                        if int(conf) > 0:
                            text_blocks.append(data['text'][i])
                            confidences.append(int(conf))
                    
                    text = ' '.join(text_blocks)
                    confidence = (sum(confidences) / len(confidences)) / 100 if confidences else 0.3
                    
                    logger.info(f"Tesseract OCR completed with {confidence:.2%} confidence")
                    return text, confidence
                    
                except Exception as tesseract_error:
                    logger.error(f"Tesseract also failed: {tesseract_error}")
                    raise Exception("OCR failed with both Textract and Tesseract")
                    
        except Exception as e:
            logger.error(f"Error extracting text from grade sheet: {str(e)}")
            raise
    
    def _extract_grades(self, text: str) -> List[Dict]:
        """
        Extract individual grades from text using pattern matching.
        
        Args:
            text: OCR extracted text
            
        Returns:
            List of grade dictionaries with subject and grade
        """
        grades = []
        
        # Common grade patterns
        patterns = [
            # "Mathematics: 95" or "Math 95"
            r'([A-Za-z\s]+)[\s:]+(\d{2,3})',
            # "Math - 1.25" (GWA format)
            r'([A-Za-z\s]+)[\s\-:]+(\d\.\d{2})',
            # "95 Mathematics" (reverse order)
            r'(\d{2,3})[\s]+([A-Za-z\s]{3,})',
            # "Subject: Math Grade: 95"
            r'Subject[\s:]*([A-Za-z\s]+)[\s]*Grade[\s:]*(\d{2,3})',
            # With units/credits: "Mathematics (3 units): 95"
            r'([A-Za-z\s]+)[\s]*\([0-9]\s*units?\)[\s:]*(\d{2,3})',
        ]
        
        seen_subjects = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:
                    # Determine which group is subject and which is grade
                    g1, g2 = match.groups()
                    
                    # Check if first group is numeric
                    try:
                        grade_value = float(g1)
                        subject = g2.strip()
                    except ValueError:
                        try:
                            grade_value = float(g2)
                            subject = g1.strip()
                        except ValueError:
                            continue
                    
                    # Validate subject name (must be at least 3 chars, mostly letters)
                    if len(subject) < 3 or not any(c.isalpha() for c in subject):
                        continue
                    
                    # Normalize subject name
                    subject = ' '.join(subject.split())
                    
                    # Avoid duplicates
                    if subject.lower() in seen_subjects:
                        continue
                    
                    # Validate grade range
                    if 1.0 <= grade_value <= 5.0:
                        # Already in GWA format
                        gwa_grade = grade_value
                    elif 65 <= grade_value <= 100:
                        # Convert percentage to GWA (inverted scale)
                        # 100 = 1.00, 95 = 1.50, 90 = 2.00, 85 = 2.50, 80 = 3.00, 75 = 3.50
                        gwa_grade = self._convert_percentage_to_gwa(grade_value)
                    else:
                        continue
                    
                    grades.append({
                        'subject': subject,
                        'grade': float(grade_value),
                        'gwa_equivalent': float(gwa_grade)
                    })
                    
                    seen_subjects.add(subject.lower())
        
        logger.info(f"Extracted {len(grades)} grades from document")
        return grades
    
    def _convert_percentage_to_gwa(self, percentage: float) -> float:
        """
        Convert percentage grade (65-100) to GWA scale (1.00-5.00).
        
        Args:
            percentage: Grade in percentage (65-100)
            
        Returns:
            GWA equivalent (1.00-5.00)
        """
        if percentage >= 97:
            return 1.00
        elif percentage >= 94:
            return 1.25
        elif percentage >= 91:
            return 1.50
        elif percentage >= 88:
            return 1.75
        elif percentage >= 85:
            return 2.00
        elif percentage >= 82:
            return 2.25
        elif percentage >= 79:
            return 2.50
        elif percentage >= 76:
            return 2.75
        elif percentage >= 75:
            return 3.00
        else:
            return 5.00  # Failed
    
    def _calculate_gwa(self, grades: List[Dict]) -> Decimal:
        """
        Calculate General Weighted Average from grades.
        
        Args:
            grades: List of grade dictionaries
            
        Returns:
            Calculated GWA (Decimal for precision)
        """
        if not grades:
            return Decimal('0.00')
        
        total = sum(g['gwa_equivalent'] for g in grades)
        gwa = Decimal(str(total / len(grades)))
        
        # Round to 2 decimal places
        gwa = gwa.quantize(Decimal('0.01'))
        
        logger.info(f"Calculated GWA: {gwa} from {len(grades)} subjects")
        return gwa
    
    def _determine_merit_level(self, gwa: Decimal) -> str:
        """
        Determine merit level based on GWA.
        
        Args:
            gwa: General Weighted Average
            
        Returns:
            Merit level classification
        """
        gwa_float = float(gwa)
        
        if gwa_float <= self.MERIT_THRESHOLDS['HIGH_HONORS']:
            return 'HIGH_HONORS'
        elif gwa_float <= self.MERIT_THRESHOLDS['HONORS']:
            return 'HONORS'
        elif gwa_float <= self.MERIT_THRESHOLDS['MERIT']:
            return 'MERIT'
        elif gwa_float <= self.MERIT_THRESHOLDS['REGULAR']:
            return 'REGULAR'
        else:
            return 'NOT_QUALIFIED'
    
    def _generate_recommendations(
        self, 
        gwa: Decimal, 
        merit_level: str, 
        grades: List[Dict]
    ) -> List[str]:
        """
        Generate personalized recommendations based on academic performance.
        
        Args:
            gwa: General Weighted Average
            merit_level: Determined merit level
            grades: List of grade dictionaries
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Merit-based recommendations
        if merit_level == 'HIGH_HONORS':
            recommendations.append('🏆 Outstanding academic performance! You qualify for the highest scholarship tier.')
            recommendations.append('💡 Consider applying for additional honors scholarships.')
        elif merit_level == 'HONORS':
            recommendations.append('⭐ Excellent academic performance! You qualify for honors scholarship.')
            recommendations.append('💡 Keep up the good work to maintain your scholarship eligibility.')
        elif merit_level == 'MERIT':
            recommendations.append('✅ Good academic performance! You qualify for merit-based scholarship.')
            recommendations.append('💡 Focus on improving grades to qualify for honors level.')
        elif merit_level == 'REGULAR':
            recommendations.append('📚 You meet the minimum academic requirements for scholarship consideration.')
            recommendations.append('💡 Work on improving your GWA to qualify for merit levels.')
        else:
            recommendations.append('⚠️ Your current GWA does not meet scholarship requirements.')
            recommendations.append('💡 Focus on academic improvement and consider reapplying next term.')
        
        # Identify weak subjects
        if grades:
            weak_grades = [g for g in grades if g['gwa_equivalent'] > 2.5]
            if weak_grades:
                weak_subjects = ', '.join(g['subject'] for g in weak_grades[:3])
                recommendations.append(f'📖 Consider additional support in: {weak_subjects}')
        
        # GWA proximity to threshold
        gwa_float = float(gwa)
        if merit_level == 'REGULAR' and gwa_float <= 3.20:
            recommendations.append('🎯 You are close to MERIT level! Improve by 0.20 points.')
        elif merit_level == 'MERIT' and gwa_float <= 2.70:
            recommendations.append('🎯 You are close to HONORS level! Improve by 0.20 points.')
        
        return recommendations
