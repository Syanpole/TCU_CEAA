/**
 * AWS Rekognition Face Liveness Service
 * 
 * Provides frontend integration with backend AWS Rekognition liveness flow:
 * 1. Create liveness session on backend
 * 2. User completes 3D liveness challenge (AWS Amplify or backend-rendered)
 * 3. Complete verification with backend (liveness + face comparison)
 * 
 * Security: All verifications require mandatory admin review
 */

import axios, { AxiosError } from 'axios';

// Extended timeout for cross-cloud processing (Google Cloud → AWS)
const LIVENESS_TIMEOUT = 60000; // 60 seconds

export interface LivenessSessionResponse {
  success: boolean;
  session_id?: string;
  error?: string;
}

export interface LivenessVerificationResponse {
  success: boolean;
  liveness_passed: boolean;
  face_match: boolean;
  similarity_score: number;
  similarity_percentage: number;
  confidence: string;
  requires_admin_review: boolean;
  adjudication_id: number;
  adjudication_status: string;
  message: string;
  error?: string;
}

/**
 * Create a new AWS Rekognition Face Liveness session
 * 
 * @returns Promise with session_id for frontend liveness UI
 */
export const startLivenessSession = async (): Promise<LivenessSessionResponse> => {
  try {
    const response = await axios.post<LivenessSessionResponse>(
      '/api/face-verification/create-liveness-session/',
      {},
      {
        timeout: LIVENESS_TIMEOUT,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('Failed to create liveness session:', error);
    
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<LivenessSessionResponse>;
      return {
        success: false,
        error: axiosError.response?.data?.error || 'Failed to create liveness session',
      };
    }

    return {
      success: false,
      error: 'Network error creating liveness session',
    };
  }
};

/**
 * Complete biometric verification: Liveness + Identity Match
 * 
 * This function should be called AFTER the user completes the 3D liveness challenge.
 * It verifies the liveness results and compares the reference image against the School ID.
 * 
 * @param sessionId - Session ID from startLivenessSession
 * @param schoolIdFile - School ID image file for comparison
 * @param applicationId - Optional AllowanceApplication ID to link verification
 * @returns Promise with verification results (always pending admin review)
 */
export const completeLivenessChallenge = async (
  sessionId: string,
  schoolIdFile: File,
  applicationId?: number
): Promise<LivenessVerificationResponse> => {
  try {
    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('school_id_image', schoolIdFile);
    
    if (applicationId) {
      formData.append('application_id', applicationId.toString());
    }

    const response = await axios.post<LivenessVerificationResponse>(
      '/api/face-verification/verify-with-liveness/',
      formData,
      {
        timeout: LIVENESS_TIMEOUT,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  } catch (error) {
    console.error('Liveness verification failed:', error);
    
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<LivenessVerificationResponse>;
      
      // Return error response from backend if available
      if (axiosError.response?.data) {
        return axiosError.response.data;
      }
      
      return {
        success: false,
        liveness_passed: false,
        face_match: false,
        similarity_score: 0,
        similarity_percentage: 0,
        confidence: 'very_low',
        requires_admin_review: true,
        adjudication_id: 0,
        adjudication_status: 'error',
        message: 'Verification failed',
        error: axiosError.response?.data?.error || axiosError.message || 'Verification request failed',
      };
    }

    return {
      success: false,
      liveness_passed: false,
      face_match: false,
      similarity_score: 0,
      similarity_percentage: 0,
      confidence: 'very_low',
      requires_admin_review: true,
      adjudication_id: 0,
      adjudication_status: 'error',
      message: 'Verification failed',
      error: 'Network error during verification',
    };
  }
};

/**
 * Check if liveness verification is enabled on the backend
 * 
 * @returns Promise indicating whether AWS Rekognition is configured
 */
export const isLivenessEnabled = async (): Promise<boolean> => {
  try {
    // Try to create a test session (will fail gracefully if not enabled)
    const result = await startLivenessSession();
    return result.success || (result.error && !result.error.includes('not enabled'));
  } catch {
    return false;
  }
};

export default {
  startLivenessSession,
  completeLivenessChallenge,
  isLivenessEnabled,
};
