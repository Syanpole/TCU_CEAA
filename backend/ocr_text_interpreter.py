"""
Intelligent OCR Text Interpreter
Uses context clues, fuzzy matching, and pattern recognition to interpret garbled OCR text
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional


class OCRTextInterpreter:
    """
    Intelligent interpreter that makes educated guesses about what garbled OCR text actually means.
    Uses context clues like:
    - Common patterns (e.g., "Computer Science" → likely a degree program)
    - Structural hints (e.g., numbers after "Year" → year level)
    - Fuzzy string matching for known values
    - Position/sequence context
    """
    
    def __init__(self):
        # Known TCU courses/programs
        self.known_programs = {
            'computer science': 'Bachelor of Science in Computer Science',
            'information technology': 'Bachelor of Science in Information Technology',
            'business administration': 'Bachelor of Science in Business Administration',
            'nursing': 'Bachelor of Science in Nursing',
            'education': 'Bachelor of Elementary Education',
            'engineering': 'Bachelor of Science in Engineering',
            'accountancy': 'Bachelor of Science in Accountancy',
            'hospitality': 'Bachelor of Science in Hospitality Management'
        }
        
        # Common OCR misreads
        self.common_ocr_errors = {
            'kepublic': 'republic',
            'epublic': 'republic',
            'peilippines': 'philippines',
            'prilippines': 'philippines',
            'taguig': 'taguig',
            'universiry': 'university',
            'universi': 'university',
            'enrollmem': 'enrollment',
            'enrolment': 'enrollment',
            'cerrificare': 'certificate',
            'srudent': 'student',
            'noone': 'no',
            'yearlevel': 'year level',
            'cotte': 'college',
            'depanment': 'department',
            'departmem': 'department',
            'semesrer': 'semester',
            'firsr': 'first',
            'validared': 'validated',
            'enrolleo': 'enrolled'
        }
        
        # Document structure patterns
        self.structure_patterns = {
            'header': ['republic', 'philippines', 'taguig', 'university', 'certificate', 'enrollment'],
            'student_info': ['student', 'name', 'number', 'id', 'year', 'level', 'course'],
            'semester_info': ['semester', 'school year', 'academic year', 'first', 'second'],
            'validation': ['enrolled', 'validated', 'registrar', 'approved']
        }
    
    def fuzzy_match(self, text: str, target: str, threshold: float = 0.6) -> float:
        """Calculate fuzzy string similarity (0-1)"""
        return SequenceMatcher(None, text.lower(), target.lower()).ratio()
    
    def clean_ocr_text(self, text: str) -> str:
        """Clean common OCR errors"""
        text_lower = text.lower()
        for error, correction in self.common_ocr_errors.items():
            text_lower = text_lower.replace(error, correction)
        return text_lower
    
    def interpret_program(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret course/program from text
        
        Examples:
        - "Computer Science" → Bachelor of Science in Computer Science
        - "Cotte OF Of Science in Computer Science" → Bachelor of Science in Computer Science
        """
        cleaned = self.clean_ocr_text(text)
        
        # Check for known programs
        for keyword, full_name in self.known_programs.items():
            if keyword in cleaned:
                return {
                    'field': 'program',
                    'raw_text': text,
                    'interpreted_value': full_name,
                    'confidence': 0.85,
                    'reasoning': f'Found "{keyword}" keyword → likely {full_name}',
                    'method': 'keyword_match'
                }
        
        # Check for degree patterns (Bachelor, B.S., etc.)
        if 'bachelor' in cleaned or 'b.s.' in cleaned or 'science' in cleaned:
            # Try to extract the field name
            if 'computer' in cleaned:
                return {
                    'field': 'program',
                    'raw_text': text,
                    'interpreted_value': 'Bachelor of Science in Computer Science',
                    'confidence': 0.80,
                    'reasoning': 'Found "computer" + "science" → likely Computer Science degree',
                    'method': 'pattern_match'
                }
        
        return None
    
    def interpret_year_level(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret year level from text
        
        Examples:
        - "Yearlevel : 4" → 4th year
        - "Year level 2" → 2nd year
        """
        cleaned = self.clean_ocr_text(text)
        
        # Look for year level patterns
        year_pattern = r'year\s*level?\s*:?\s*(\d+)'
        match = re.search(year_pattern, cleaned)
        
        if match:
            year = int(match.group(1))
            ordinal = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th'}.get(year, f'{year}th')
            return {
                'field': 'year_level',
                'raw_text': text,
                'interpreted_value': year,
                'display_value': f'{ordinal} year',
                'confidence': 0.90,
                'reasoning': f'Found "year level : {year}" → {ordinal} year student',
                'method': 'regex_pattern'
            }
        
        # Fallback: look for any digit after "year"
        year_fallback = r'year[^\d]*(\d+)'
        match2 = re.search(year_fallback, cleaned)
        if match2:
            year = int(match2.group(1))
            if 1 <= year <= 6:  # Valid year range
                ordinal = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th', 6: '6th'}.get(year, f'{year}th')
                return {
                    'field': 'year_level',
                    'raw_text': text,
                    'interpreted_value': year,
                    'display_value': f'{ordinal} year',
                    'confidence': 0.75,
                    'reasoning': f'Found digit {year} near "year" → likely {ordinal} year',
                    'method': 'fuzzy_pattern'
                }
        
        return None
    
    def interpret_student_name(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret student name from text
        
        Examples:
        - "Course, 'Ramos, Lloyd Kenneth S." → Ramos, Lloyd Kenneth S.
        - "Student Name: Dela Cruz, Juan" → Dela Cruz, Juan
        """
        cleaned = text.strip()
        
        # First, try to extract name that might be embedded in a line with other text
        # Pattern: Look for "Lastname, Firstname Middlename Initial" format anywhere in text
        embedded_name_pattern = r"['\"]?\s*([A-Z][a-z]{2,15},\s+[A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15})*(?:\s+[A-Z]\.)?)\s*"
        embedded_match = re.search(embedded_name_pattern, cleaned)
        
        if embedded_match:
            potential_name = embedded_match.group(1)
            # Verify it's not a false positive (check for common last names or name-like structure)
            words = potential_name.split(',')[0].strip()
            # If the first part (last name) is reasonable length
            if 3 <= len(words) <= 20:
                return {
                    'field': 'student_name',
                    'raw_text': text,
                    'interpreted_value': potential_name,
                    'confidence': 0.85,
                    'reasoning': f'Found name pattern (Last, First Middle) embedded in line → {potential_name}',
                    'method': 'embedded_extraction'
                }
        
        # Skip lines that are clearly not names
        skip_keywords = ['certificate', 'enrollment', 'semester', 'department', 'college', 
                        'university', 'republic', 'taguig']
        if any(keyword in cleaned.lower() for keyword in skip_keywords):
            return None
        
        # Pattern 1: Name with comma (Last, First Middle)
        # Look for: Word, Word Word (possibly with initials)
        name_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.?)?)"
        match = re.search(name_pattern, cleaned)
        
        if match:
            last_name = match.group(1)
            first_middle = match.group(2)
            full_name = f"{last_name}, {first_middle}"
            
            return {
                'field': 'student_name',
                'raw_text': text,
                'interpreted_value': full_name,
                'last_name': last_name,
                'first_middle': first_middle,
                'confidence': 0.85,
                'reasoning': f'Found name pattern "Last, First Middle" → {full_name}',
                'method': 'regex_pattern'
            }
        
        # Pattern 2: Look for capitalized words that might be a name
        # Usually appears after "Student Name:" or near student info
        words = cleaned.split()
        cap_words = [w for w in words if w and w[0].isupper() and len(w) > 2 and w not in 
                     ['Course', 'Department', 'Student', 'Name', 'Year', 'Level', 'Enrollment', 'Date']]
        
        if len(cap_words) >= 2:
            # Check if it looks like a name (has comma or multiple capitalized words)
            potential_name = ' '.join(cap_words)
            if ',' in potential_name:
                return {
                    'field': 'student_name',
                    'raw_text': text,
                    'interpreted_value': potential_name.strip(',\'\" '),
                    'confidence': 0.70,
                    'reasoning': f'Found capitalized words with comma → likely name: {potential_name}',
                    'method': 'heuristic'
                }
        
        return None
    
    def interpret_student_id(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret student ID from text
        
        Examples:
        - "Student No: 19-00648" → 19-00648
        - "Student Noone res 19-00648" → 19-00648
        - "ID: 2019-00123" → 2019-00123
        """
        cleaned = text.strip()
        
        # Skip if this looks like a year range (semester dates)
        if 'semester' in cleaned.lower() or ('20' in cleaned and '-20' in cleaned and len(cleaned) < 50):
            return None
        
        # Pattern 1: Standard format (2-4 digits, dash, 4-5 digits)
        id_pattern = r'\b(\d{2,4}[-]\d{4,5})\b'
        match = re.search(id_pattern, cleaned)
        
        if match:
            student_id = match.group(1)
            # Verify it's not a year range (2025-2026)
            if len(student_id) > 9 and student_id.startswith('20'):
                return None
            
            # Must have "student" or "no" nearby to be confident
            has_student_keyword = 'student' in cleaned.lower() or 'no' in cleaned.lower() or 'id' in cleaned.lower()
            
            return {
                'field': 'student_id',
                'raw_text': text,
                'interpreted_value': student_id,
                'confidence': 0.90 if has_student_keyword else 0.60,
                'reasoning': f'Found ID pattern (##-#####) → {student_id}' + (' near "student" keyword' if has_student_keyword else ''),
                'method': 'regex_pattern'
            }
        
        # Pattern 2: Without dash (but near "student" keyword)
        if 'student' in text.lower() or 'no' in text.lower():
            # Look for 6-9 digit number
            id_fallback = r'\b(\d{6,9})\b'
            match2 = re.search(id_fallback, cleaned)
            if match2:
                raw_id = match2.group(1)
                # Try to format it (assume first 2 digits are year)
                if len(raw_id) == 7:
                    formatted_id = f"{raw_id[:2]}-{raw_id[2:]}"
                    return {
                        'field': 'student_id',
                        'raw_text': text,
                        'interpreted_value': formatted_id,
                        'confidence': 0.70,
                        'reasoning': f'Found 7-digit number near "student" → formatted as {formatted_id}',
                        'method': 'fuzzy_pattern'
                    }
        
        return None
    
    def interpret_semester(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret semester information
        
        Examples:
        - "First Semester 2025-2026" → First Semester, AY 2025-2026
        - "Second Semester 2024-2025" → Second Semester, AY 2024-2025
        """
        cleaned = self.clean_ocr_text(text)
        
        # Look for semester (First/Second) and year (YYYY-YYYY)
        semester_pattern = r'(first|second|1st|2nd)\s+semester\s+(\d{4})\s*[-/]\s*(\d{4})'
        match = re.search(semester_pattern, cleaned)
        
        if match:
            sem_type = match.group(1)
            year_start = match.group(2)
            year_end = match.group(3)
            
            # Fix common OCR year errors (2125 → 2025)
            year_start_corrected = self._correct_year_ocr_errors(year_start)
            year_end_corrected = self._correct_year_ocr_errors(year_end)
            
            # Normalize semester name
            sem_name = 'First Semester' if 'first' in sem_type or '1st' in sem_type else 'Second Semester'
            
            # Build reasoning with correction note if needed
            reasoning = f'Found semester pattern → {sem_name}, Academic Year {year_start_corrected}-{year_end_corrected}'
            if year_start != year_start_corrected or year_end != year_end_corrected:
                reasoning += f' (corrected OCR misread: {year_start}-{year_end} → {year_start_corrected}-{year_end_corrected})'
            
            return {
                'field': 'semester',
                'raw_text': text,
                'interpreted_value': f'{sem_name}, AY {year_start_corrected}-{year_end_corrected}',
                'semester': sem_name,
                'academic_year': f'{year_start_corrected}-{year_end_corrected}',
                'confidence': 0.85,
                'reasoning': reasoning,
                'method': 'regex_pattern'
            }
        
        return None
    
    def _correct_year_ocr_errors(self, year_str: str) -> str:
        """
        Correct common OCR errors in year numbers.
        
        Common OCR mistakes:
        - 2025 → 2125 (0 misread as 1)
        - 2026 → 2126 (0 misread as 1)
        """
        try:
            year = int(year_str)
            
            # If year is in 2100s (like 2125), OCR likely misread 2025 as 2125
            # This happens when OCR confuses 0 with 1
            if 2100 <= year <= 2199:
                # Replace the '1' in position 2 with '0'
                corrected = '20' + year_str[2:]
                return corrected
            
            # If year is unreasonably far in the future (beyond 2050)
            # Try to fix by replacing third digit
            current_year = 2025
            if year > 2050 and year < 2200:
                # Try replacing digit at position 2 with 0
                test_year = int('20' + year_str[2:])
                if 2000 <= test_year <= current_year + 10:
                    return str(test_year)
            
            return year_str
        except (ValueError, IndexError):
            # If conversion fails, return original
            return year_str
    
    def interpret_enrollment_date(self, text: str) -> Optional[Dict[str, any]]:
        """
        Interpret enrollment date
        
        Examples:
        - "Enrollment Date: 07/05/2025" → July 5, 2025
        """
        # Look for date pattern (MM/DD/YYYY or DD/MM/YYYY)
        date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(date_pattern, text)
        
        if match:
            part1 = match.group(1)
            part2 = match.group(2)
            year = match.group(3)
            
            # Fix common OCR year errors
            year_corrected = self._correct_year_ocr_errors(year)
            
            reasoning = f'Found date pattern → {part1}/{part2}/{year_corrected}'
            if year != year_corrected:
                reasoning += f' (corrected OCR misread: {year} → {year_corrected})'
            
            return {
                'field': 'enrollment_date',
                'raw_text': text,
                'interpreted_value': f'{part1}/{part2}/{year_corrected}',
                'confidence': 0.90,
                'reasoning': reasoning,
                'method': 'regex_pattern'
            }
        
        return None
    
    def interpret_document_text(self, full_text: str) -> Dict[str, any]:
        """
        Interpret the entire OCR text and extract structured information
        
        Returns a dictionary of interpreted fields with confidence scores and reasoning
        """
        lines = full_text.split('\n')
        interpretations = {
            'program': None,
            'year_level': None,
            'student_name': None,
            'student_id': None,
            'semester': None,
            'enrollment_date': None,
            'all_interpretations': []
        }
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Try ALL interpretation methods for this line (not just first match)
            # This way we can extract multiple pieces of info from one line
            interp_methods = [
                self.interpret_student_name,
                self.interpret_student_id,
                self.interpret_year_level,
                self.interpret_program,
                self.interpret_semester,
                self.interpret_enrollment_date
            ]
            
            for method in interp_methods:
                try:
                    interp = method(line_clean)
                    if interp:
                        field = interp['field']
                        # Only update if not already found or if new confidence is higher
                        if interpretations[field] is None or interp['confidence'] > interpretations[field]['confidence']:
                            interpretations[field] = interp
                        interpretations['all_interpretations'].append(interp)
                except:
                    pass  # Skip errors
            
            # OLD CODE - only found first match per line:
            # interp = (
            #     self.interpret_program(line_clean) or
            #     self.interpret_year_level(line_clean) or
            #     self.interpret_student_name(line_clean) or
            #     self.interpret_student_id(line_clean) or
            #     self.interpret_semester(line_clean) or
            #     self.interpret_enrollment_date(line_clean)
            # )

        
        return interpretations
    
    def generate_interpretation_report(self, interpretations: Dict) -> str:
        """Generate a human-readable report of interpretations"""
        report = []
        report.append("=" * 80)
        report.append("🧠 INTELLIGENT OCR INTERPRETATION")
        report.append("=" * 80)
        report.append("")
        
        fields = ['student_name', 'student_id', 'program', 'year_level', 'semester', 'enrollment_date']
        
        for field in fields:
            interp = interpretations.get(field)
            if interp:
                field_display = field.replace('_', ' ').title()
                report.append(f"📋 {field_display}:")
                report.append(f"   Raw OCR: {interp['raw_text'][:60]}")
                
                if 'display_value' in interp:
                    report.append(f"   ✨ Interpreted: {interp['display_value']}")
                else:
                    report.append(f"   ✨ Interpreted: {interp['interpreted_value']}")
                
                report.append(f"   📊 Confidence: {interp['confidence']:.0%}")
                report.append(f"   💡 Reasoning: {interp['reasoning']}")
                report.append("")
        
        # Summary
        found_count = sum(1 for field in fields if interpretations.get(field))
        report.append("=" * 80)
        report.append(f"✅ Successfully interpreted {found_count} out of {len(fields)} fields")
        report.append("=" * 80)
        
        return '\n'.join(report)


# Example usage
if __name__ == "__main__":
    # Example garbled OCR text
    garbled_text = """
    AOF Tad epublic of ine peilippines Ky mn ~
    es City Universi  . Faay
    o Et Taguig City University fe LZ g
    SE, CERTIFICATE OF ENROLLMENT } Om lS i
    H ood py teppei?" ah .
    First Semester 2125-2026 oy ee 'sy ee ' FE E
    Student Noone res Enrollment Date: 07/05/2025 1 iaGuig r La; =,
    Course, 'Ramos, Lloyd Kenneth S. Yearlevel : 4 aon -? g ON:
    Department: Cotte OF Of Science in Computer Science
    """
    
    print("=" * 80)
    print("🔍 DEBUGGING: Checking name extraction")
    print("=" * 80)
    test_line = "Course, 'Ramos, Lloyd Kenneth S. Yearlevel : 4 aon -? g ON:"
    print(f"Test line: {test_line}")
    
    import re
    pattern = r"['\"]?\s*([A-Z][a-z]{2,15},\s+[A-Z][a-z]{2,15}(?:\s+[A-Z][a-z]{2,15})*(?:\s+[A-Z]\.)?)\s*"
    match = re.search(pattern, test_line)
    if match:
        print(f"✅ Match found: {match.group(1)}")
    else:
        print("❌ No match found")
        # Try simpler pattern
        simple_pattern = r"([A-Z][a-z]+,\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.)?)"
        match2 = re.search(simple_pattern, test_line)
        if match2:
            print(f"✅ Simple pattern match: {match2.group(1)}")
    print("="* 80)
    print()
    
    interpreter = OCRTextInterpreter()
    results = interpreter.interpret_document_text(garbled_text)
    
    print(interpreter.generate_interpretation_report(results))
    
    print("\n" + "=" * 80)
    print("🎯 EXTRACTED DATA SUMMARY")
    print("=" * 80)
    
    if results['student_name']:
        print(f"Student: {results['student_name']['interpreted_value']}")
    if results['student_id']:
        print(f"ID: {results['student_id']['interpreted_value']}")
    if results['program']:
        print(f"Program: {results['program']['interpreted_value']}")
    if results['year_level']:
        print(f"Year: {results['year_level']['display_value']}")
    if results['semester']:
        print(f"Semester: {results['semester']['interpreted_value']}")
