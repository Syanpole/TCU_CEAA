import { apiClient } from './authService';

export interface DocumentStatus {
  id: number;
  document_type: string;
  document_type_display: string;
  status: string;
  status_display: string;
  submitted_at: string;
}

export interface GradeSubmissionEligibility {
  canSubmit: boolean;
  requiredDocuments: string[];
  missingDocuments: string[];
  pendingDocuments: string[];
  approvedDocuments: string[];
}

export const documentService = {
  // Get all user documents
  async getUserDocuments(): Promise<DocumentStatus[]> {
    try {
      const response = await apiClient.get('/documents/');
      const data = response.data as any;
      return data.results || data;
    } catch (error) {
      console.error('Error fetching documents:', error);
      // Return mock data for demo
      return [
        {
          id: 1,
          document_type: 'certificate_of_enrollment',
          document_type_display: 'Certificate of Enrollment',
          status: 'pending',
          status_display: 'Under Review',
          submitted_at: '2025-08-20T10:00:00Z'
        },
        {
          id: 2,
          document_type: 'birth_certificate',
          document_type_display: 'Birth Certificate',
          status: 'approved',
          status_display: 'Approved',
          submitted_at: '2025-08-19T14:30:00Z'
        }
      ];
    }
  },

  // Check if user can submit grades
  async checkGradeSubmissionEligibility(): Promise<GradeSubmissionEligibility> {
    try {
      const documents = await this.getUserDocuments();
      
      // Dynamic required documents based on what user has submitted
      // We consider any relevant academic/enrollment documents as valid
      const validDocumentTypes = [
        'certificate_of_enrollment',
        'enrollment_certificate',
        'birth_certificate',
        'school_id',
        'grade_10_report_card',
        'grade_12_report_card',
        'transcript_of_records',
        'diploma',
        'report_card',
        'academic_records',
        'valid_id',
        'junior_hs_certificate',
        'senior_hs_diploma'
      ];
      
      // Filter documents that are valid for grade submission
      const submittedValidDocs = documents.filter(doc => 
        validDocumentTypes.includes(doc.document_type)
      );
      
      const approvedDocuments = submittedValidDocs
        .filter(doc => doc.status === 'approved')
        .map(doc => doc.document_type);
      
      const pendingDocuments = submittedValidDocs
        .filter(doc => doc.status === 'pending')
        .map(doc => doc.document_type);
      
      const submittedDocTypes = submittedValidDocs.map(doc => doc.document_type);
      
      // Determine required documents based on what they've submitted
      let requiredDocuments: string[] = [];
      
      if (submittedDocTypes.length === 0) {
        // If no documents submitted yet, suggest basic requirements
        requiredDocuments = ['certificate_of_enrollment', 'birth_certificate'];
      } else {
        // Use the documents they've already submitted as requirements
        requiredDocuments = submittedDocTypes;
      }
      
      const missingDocuments = requiredDocuments.filter(
        docType => !submittedDocTypes.includes(docType)
      );
      
      // Can submit if at least one valid document is approved
      const canSubmit = approvedDocuments.length > 0;
      
      return {
        canSubmit,
        requiredDocuments,
        missingDocuments,
        pendingDocuments,
        approvedDocuments
      };
    } catch (error) {
      console.error('Error checking grade submission eligibility:', error);
      return {
        canSubmit: false,
        requiredDocuments: ['certificate_of_enrollment', 'birth_certificate'],
        missingDocuments: ['certificate_of_enrollment', 'birth_certificate'],
        pendingDocuments: [],
        approvedDocuments: []
      };
    }
  },

  // Document type labels - SYNCED WITH BACKEND
  getDocumentTypeLabel(documentType: string): string {
    const labels: { [key: string]: string } = {
      // Simplified Required Documents
      academic_records: 'Academic Records (Grade 10/12 Report Card, Certificate, or Diploma)',
      valid_id: 'Valid ID (School ID, Birth Certificate, or Government-issued ID)',
      certificate_of_enrollment: 'Certificate of Enrollment',
      transcript_of_records: 'Transcript of Records',
      
      // Required Documents (New Applicants)
      junior_hs_certificate: 'Junior High School Certificate/Grade 10 Report Card',
      senior_hs_diploma: 'Senior High School Diploma/Grade 12 Report Card',
      school_id: 'School ID or Valid Government-issued ID',
      birth_certificate: 'Birth Certificate (PSA/NSO/Civil Registry)',
      grade_10_report_card: 'Grade 10 Report Card',
      grade_12_report_card: 'Grade 12 Report Card',
      diploma: 'Diploma',
      
      // Other Necessary Documents
      form_137: 'Form 137 (Certified True Copy)',
      als_certificate: 'ALS Certificate',
      death_certificate: 'Death Certificate (PSA/NSO/Civil Registry)',
      work_contract_visa: 'Work Contract/VISA/Passport (OFW)',
      comelec_stub: 'Comelec Stub (after May 2022)',
      
      // Valid Government-issued IDs
      umid_card: 'UMID Card',
      drivers_license: 'Driver\'s License',
      passport: 'Passport',
      sss_id: 'SSS ID',
      voters_id: 'Voter\'s ID',
      bir_tin_id: 'BIR (TIN) ID',
      pag_ibig_id: 'Pag-IBIG ID',
      company_id: 'Company ID',
      postal_id: 'Postal ID',
      philhealth_id: 'PhilHealth ID',
      philsys_id: 'Philippine National ID (PhilSys)',
      afp_beneficiary_id: 'AFP Beneficiary/Dependent\'s ID',
      
      // Legacy support
      enrollment_certificate: 'Certificate of Enrollment',
      report_card: 'Report Card/Grades',
      barangay_clearance: 'Barangay Clearance',
      parents_id: 'Parent\'s Valid ID',
      voter_certification: 'Voter\'s Certification',
      other: 'Other Document',
      others: 'Others'
    };
    return labels[documentType] || documentType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  },

  // Status color helper
  getStatusColor(status: string): string {
    switch (status) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'pending': return '#f59e0b';
      case 'revision_needed': return '#8b5cf6';
      default: return '#6b7280';
    }
  }
};

export default documentService;
