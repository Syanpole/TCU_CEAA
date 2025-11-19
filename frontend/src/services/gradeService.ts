import { apiClient } from './authService';

// Types for grade submission workflow
export interface COESubject {
  subject_code: string;
  subject_name: string;
}

export interface COESubjectsResponse {
  subjects: COESubject[];
  subject_count: number;
  coe_document_id: number;
  academic_year?: string;
  semester?: string;
}

export interface SubjectGradeSubmission {
  subject_code: string;
  subject_name: string;
  academic_year: string;
  semester: string;
  units: number;
  grade_received: number;
  grade_sheet: File;
}

export interface GradeSubmissionRecord {
  id: number;
  subject_code: string;
  subject_name: string;
  units: number;
  grade_received: number;
  grade_sheet: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  admin_notes?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  matched_subjects: Array<{
    coe_code: string;
    coe_name: string;
    submission_code: string;
    submission_name: string;
    similarity: number;
  }>;
  missing_subjects: Array<{
    subject_code: string;
    subject_name: string;
  }>;
  extra_subjects: Array<{
    subject_code: string;
    subject_name: string;
  }>;
  errors: string[];
  warnings: string[];
}

export interface GradeSubmissionStatus {
  total_subjects: number;
  submitted_count: number;
  approved_count: number;
  pending_count: number;
  rejected_count: number;
  can_proceed_to_liveness: boolean;
  gpa_calculated: boolean;
  general_weighted_average?: number;
  submissions: GradeSubmissionRecord[];
}

export const gradeService = {
  /**
   * Fetch COE subjects for the current user
   */
  getCOESubjects: async (): Promise<COESubjectsResponse> => {
    try {
      const response = await apiClient.get<COESubjectsResponse>('/grade-workflow/coe-subjects/');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching COE subjects:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        'Failed to fetch COE subjects. Please ensure you have an approved Certificate of Enrollment.'
      );
    }
  },

  /**
   * Submit grade for a single subject
   */
  submitSubjectGrade: async (gradeData: SubjectGradeSubmission): Promise<GradeSubmissionRecord> => {
    try {
      const formData = new FormData();
      formData.append('subject_code', gradeData.subject_code);
      formData.append('subject_name', gradeData.subject_name);
      formData.append('academic_year', gradeData.academic_year);
      formData.append('semester', gradeData.semester);
      formData.append('units', gradeData.units.toString());
      formData.append('grade_received', gradeData.grade_received.toString());
      formData.append('grade_sheet', gradeData.grade_sheet);

      const response = await apiClient.post<GradeSubmissionRecord>(
        '/grade-workflow/submit-subject/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error submitting subject grade:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        error.response?.data?.grade_sheet?.[0] ||
        'Failed to submit grade for this subject.'
      );
    }
  },

  /**
   * Validate all grade submissions against COE
   */
  validateGradeSubmissions: async (academicYear: string, semester: string): Promise<ValidationResult> => {
    try {
      const response = await apiClient.post<ValidationResult>('/grade-workflow/validate/', {
        academic_year: academicYear,
        semester: semester,
      });
      return response.data;
    } catch (error: any) {
      console.error('Error validating grade submissions:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        'Failed to validate grade submissions.'
      );
    }
  },

  /**
   * Get grade submission status and progress
   */
  getGradeSubmissionStatus: async (academicYear?: string, semester?: string): Promise<GradeSubmissionStatus> => {
    try {
      const params: any = {};
      if (academicYear) params.academic_year = academicYear;
      if (semester) params.semester = semester;

      const response = await apiClient.get<GradeSubmissionStatus>('/grade-workflow/status/', { params });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching grade submission status:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        'Failed to fetch grade submission status.'
      );
    }
  },

  /**
   * Delete a grade submission (before admin approval)
   */
  deleteGradeSubmission: async (submissionId: number): Promise<void> => {
    try {
      await apiClient.delete(`/grades/${submissionId}/`);
    } catch (error: any) {
      console.error('Error deleting grade submission:', error);
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        'Failed to delete grade submission.'
      );
    }
  },
};

export default gradeService;
