import { apiClient } from './authService';

export interface ScholarshipApplication {
  id: number;
  student: number;
  is_new_applicant: boolean;
  status: string;
  ai_score?: number;
  ai_feedback?: string;
  committee_feedback?: string;
  grant_status?: string;
  created_at: string;
  updated_at: string;
  documents: ScholarshipDocument[];
}

export interface ScholarshipDocument {
  id: number;
  doc_type: string;
  file: string;
  uploaded_at: string;
}

export const scholarshipService = {
  createApplication: async (isNewApplicant: boolean): Promise<ScholarshipApplication> => {
    const response = await apiClient.post<ScholarshipApplication>('/scholarship-applications/', {
      is_new_applicant: isNewApplicant,
    });
    return response.data;
  },

  uploadDocument: async (applicationId: number, docType: string, file: File): Promise<ScholarshipDocument> => {
    const formData = new FormData();
    formData.append('application', applicationId.toString());
    formData.append('doc_type', docType);
    formData.append('file', file);
    const response = await apiClient.post<ScholarshipDocument>('/scholarship-documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getMyApplications: async (): Promise<ScholarshipApplication[]> => {
    const response = await apiClient.get<ScholarshipApplication[]>('/scholarship-applications/');
    return response.data;
  },

  getApplication: async (id: number): Promise<ScholarshipApplication> => {
    const response = await apiClient.get<ScholarshipApplication>(`/scholarship-applications/${id}/`);
    return response.data;
  },
};
