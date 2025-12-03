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

  // Check if user can submit grades (server-side check)
  async checkGradeSubmissionEligibility(): Promise<GradeSubmissionEligibility> {
    try {
      // Use backend API for real-time eligibility check
      console.log('🔍 Checking grade submission eligibility via backend...');
      const response = await apiClient.get('/grade-workflow/check-eligibility/');
      const data = response.data as any;
      
      console.log('✅ Backend eligibility response:', data);
      
      return {
        canSubmit: data.can_submit,
        requiredDocuments: data.required_documents || [],
        missingDocuments: data.missing_documents || [],
        pendingDocuments: data.pending_documents || [],
        approvedDocuments: data.approved_documents || []
      };
    } catch (error: any) {
      console.error('❌ Error checking grade submission eligibility:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      // Fallback to client-side check if backend fails
      try {
        const documents = await this.getUserDocuments();
        
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
        
        let requiredDocuments: string[] = [];
        
        if (submittedDocTypes.length === 0) {
          requiredDocuments = ['certificate_of_enrollment', 'birth_certificate'];
        } else {
          requiredDocuments = submittedDocTypes;
        }
        
        const missingDocuments = requiredDocuments.filter(
          docType => !submittedDocTypes.includes(docType)
        );
        
        const canSubmit = approvedDocuments.length > 0;
        
        return {
          canSubmit,
          requiredDocuments,
          missingDocuments,
          pendingDocuments,
          approvedDocuments
        };
      } catch (fallbackError) {
        console.error('Fallback eligibility check also failed:', fallbackError);
        return {
          canSubmit: false,
          requiredDocuments: ['certificate_of_enrollment', 'id_copy'],
          missingDocuments: ['certificate_of_enrollment', 'id_copy'],
          pendingDocuments: [],
          approvedDocuments: []
        };
      }
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
  },

  // Get submitted ID image for facial comparison
  async getSubmittedIdImage(): Promise<string | null> {
    try {
      const documents = await this.getUserDocuments();
      const idDoc = documents.find(doc => 
        (doc.document_type === 'valid_id' || 
         doc.document_type === 'school_id' ||
         doc.document_type.includes('_id')) && 
        doc.status === 'approved'
      );
      
      if (idDoc) {
        // Fetch the actual document image URL
        const response = await apiClient.get(`/documents/${idDoc.id}/`);
        const data = response.data as any;
        return data.document_image || data.file || null;
      }
      return null;
    } catch (error) {
      console.error('Error fetching submitted ID image:', error);
      return null;
    }
  }
};

export default documentService;
