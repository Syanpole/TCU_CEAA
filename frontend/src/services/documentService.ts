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
    const requiredDocuments = [
      'certificate_of_enrollment',
      'birth_certificate'
    ];

    try {
      const documents = await this.getUserDocuments();
      
      const approvedDocuments = documents
        .filter(doc => requiredDocuments.includes(doc.document_type) && doc.status === 'approved')
        .map(doc => doc.document_type);
      
      const pendingDocuments = documents
        .filter(doc => requiredDocuments.includes(doc.document_type) && doc.status === 'pending')
        .map(doc => doc.document_type);
      
      const submittedDocTypes = documents.map(doc => doc.document_type);
      const missingDocuments = requiredDocuments.filter(docType => !submittedDocTypes.includes(docType));
      
      const canSubmit = approvedDocuments.length === requiredDocuments.length;
      
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
        requiredDocuments,
        missingDocuments: requiredDocuments,
        pendingDocuments: [],
        approvedDocuments: []
      };
    }
  },

  // Document type labels
  getDocumentTypeLabel(documentType: string): string {
    const labels: { [key: string]: string } = {
      birth_certificate: 'Birth Certificate',
      school_id: 'School ID',
      report_card: 'Report Card/Grades',
      certificate_of_enrollment: 'Certificate of Enrollment',
      enrollment_certificate: 'Certificate of Enrollment', // Legacy support
      barangay_clearance: 'Barangay Clearance',
      parents_id: 'Parent\'s Valid ID',
      voter_certification: 'Voter\'s Certification',
      other: 'Other Document'
    };
    return labels[documentType] || documentType;
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
