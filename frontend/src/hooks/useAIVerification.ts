import { useState, useCallback } from 'react';
import { 
  AIVerificationResult, 
  VerificationStatus, 
  DocumentSubmission,
  FaceSubmission,
  GradeSubmission,
  MatchingField
} from '../types/scholarshipTypes';
import { 
  VERIFICATION_RULES, 
  CONFIDENCE_THRESHOLDS, 
  API_ENDPOINTS 
} from '../config/scholarshipConfig';
import { apiClient } from '../services/authService';

interface VerificationOptions {
  documentType: string;
  expectedMetadata?: Record<string, any>;
  referenceData?: any;
}

export const useAIVerification = () => {
  const [verificationResults, setVerificationResults] = useState<
    Record<string, AIVerificationResult>
  >({});
  const [isVerifying, setIsVerifying] = useState<Record<string, boolean>>({});

  // Verify document
  const verifyDocument = useCallback(async (
    submission: DocumentSubmission,
    options: VerificationOptions
  ): Promise<AIVerificationResult> => {
    const verificationId = `${options.documentType}_${Date.now()}`;
    
    try {
      setIsVerifying(prev => ({ ...prev, [verificationId]: true }));
      
      const startTime = Date.now();
      
      // Prepare form data for file upload
      const formData = new FormData();
      if (submission.fileData) {
        formData.append('file', submission.fileData);
      } else if (submission.fileUrl) {
        formData.append('fileUrl', submission.fileUrl);
      }
      formData.append('documentType', options.documentType);
      formData.append('expectedMetadata', JSON.stringify(options.expectedMetadata || {}));
      formData.append('referenceData', JSON.stringify(options.referenceData || {}));
      
      // Call AI verification API
      const response = await apiClient.post<{
        success: boolean;
        confidence: number;
        status: VerificationStatus;
        feedback: string;
        matchingFields: MatchingField[];
        flaggedReasons: string[];
        extractedData?: any;
      }>(`${API_ENDPOINTS.AI_VERIFICATION}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const processingTime = Date.now() - startTime;
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: response.data.confidence,
        status: determineVerificationStatus(response.data.confidence, response.data.flaggedReasons),
        feedback: response.data.feedback,
        matchingFields: response.data.matchingFields || [],
        flaggedReasons: response.data.flaggedReasons || [],
        verifiedAt: new Date(),
        processingTime
      };

      // Store result
      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } catch (error) {
      console.error('Document verification failed:', error);
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: 0,
        status: VerificationStatus.FAILED,
        feedback: 'Verification service error. Please try again.',
        matchingFields: [],
        flaggedReasons: ['Service unavailable'],
        verifiedAt: new Date(),
        processingTime: Date.now() - Date.now()
      };

      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } finally {
      setIsVerifying(prev => ({ ...prev, [verificationId]: false }));
    }
  }, []);

  // Verify face with liveness detection
  const verifyFace = useCallback(async (
    faceSubmission: FaceSubmission,
    referenceImageUrl?: string
  ): Promise<AIVerificationResult> => {
    const verificationId = `face_${Date.now()}`;
    
    try {
      setIsVerifying(prev => ({ ...prev, [verificationId]: true }));
      
      const startTime = Date.now();
      
      const requestData = {
        imageData: faceSubmission.imageData,
        referenceImageUrl,
        performLivenessCheck: true,
        faceMatchThreshold: VERIFICATION_RULES.faceMatchThreshold,
        livenessThreshold: VERIFICATION_RULES.livenessThreshold
      };
      
      const response = await apiClient.post<{
        confidence: number;
        faceMatch: boolean;
        livenessScore: number;
        isLive: boolean;
        feedback: string;
        flaggedReasons: string[];
      }>(`${API_ENDPOINTS.FACE_VERIFICATION}`, requestData);

      const processingTime = Date.now() - startTime;
      
      // Determine overall confidence and status
      const overallConfidence = Math.min(
        response.data.confidence,
        response.data.livenessScore
      );
      
      const matchingFields: MatchingField[] = [
        {
          field: 'face_match',
          expectedValue: 'true',
          actualValue: response.data.faceMatch.toString(),
          confidence: response.data.confidence,
          isMatch: response.data.faceMatch
        },
        {
          field: 'liveness_check',
          expectedValue: 'true',
          actualValue: response.data.isLive.toString(),
          confidence: response.data.livenessScore,
          isMatch: response.data.isLive
        }
      ];
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: overallConfidence,
        status: determineVerificationStatus(overallConfidence, response.data.flaggedReasons),
        feedback: response.data.feedback,
        matchingFields,
        flaggedReasons: response.data.flaggedReasons || [],
        verifiedAt: new Date(),
        processingTime
      };

      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } catch (error) {
      console.error('Face verification failed:', error);
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: 0,
        status: VerificationStatus.FAILED,
        feedback: 'Face verification service error. Please try again.',
        matchingFields: [],
        flaggedReasons: ['Service unavailable'],
        verifiedAt: new Date(),
        processingTime: 0
      };

      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } finally {
      setIsVerifying(prev => ({ ...prev, [verificationId]: false }));
    }
  }, []);

  // Verify grades and calculate GWA
  const verifyGrades = useCallback(async (
    grades: GradeSubmission[],
    studentId: string
  ): Promise<AIVerificationResult> => {
    const verificationId = `grades_${Date.now()}`;
    
    try {
      setIsVerifying(prev => ({ ...prev, [verificationId]: true }));
      
      const startTime = Date.now();
      
      const requestData = {
        grades: grades.map(grade => ({
          subject: grade.subject,
          grade: grade.grade,
          unit: grade.unit,
          semester: grade.semester,
          yearLevel: grade.yearLevel
        })),
        studentId,
        verificationLevel: 'strict'
      };
      
      const response = await apiClient.post<{
        confidence: number;
        gwa: number;
        totalUnits: number;
        isPassing: boolean;
        isFabricated: boolean;
        suspiciousGrades: string[];
        feedback: string;
        flaggedReasons: string[];
      }>(`${API_ENDPOINTS.GRADE_VERIFICATION}`, requestData);

      const processingTime = Date.now() - startTime;
      
      const matchingFields: MatchingField[] = [
        {
          field: 'grade_authenticity',
          expectedValue: 'authentic',
          actualValue: response.data.isFabricated ? 'fabricated' : 'authentic',
          confidence: response.data.confidence,
          isMatch: !response.data.isFabricated
        },
        {
          field: 'gwa_calculation',
          expectedValue: 'valid',
          actualValue: response.data.gwa.toString(),
          confidence: response.data.confidence,
          isMatch: response.data.isPassing
        }
      ];
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: response.data.confidence,
        status: determineGradeVerificationStatus(response.data),
        feedback: response.data.feedback,
        matchingFields,
        flaggedReasons: response.data.flaggedReasons || [],
        verifiedAt: new Date(),
        processingTime
      };

      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } catch (error) {
      console.error('Grade verification failed:', error);
      
      const result: AIVerificationResult = {
        id: verificationId,
        confidence: 0,
        status: VerificationStatus.FAILED,
        feedback: 'Grade verification service error. Please try again.',
        matchingFields: [],
        flaggedReasons: ['Service unavailable'],
        verifiedAt: new Date(),
        processingTime: 0
      };

      setVerificationResults(prev => ({
        ...prev,
        [verificationId]: result
      }));

      return result;

    } finally {
      setIsVerifying(prev => ({ ...prev, [verificationId]: false }));
    }
  }, []);

  // Get verification result by ID
  const getVerificationResult = useCallback((verificationId: string) => {
    return verificationResults[verificationId];
  }, [verificationResults]);

  // Check if verification is in progress
  const isVerificationInProgress = useCallback((verificationId: string) => {
    return isVerifying[verificationId] || false;
  }, [isVerifying]);

  // Clear verification results
  const clearVerificationResults = useCallback(() => {
    setVerificationResults({});
    setIsVerifying({});
  }, []);

  return {
    verifyDocument,
    verifyFace,
    verifyGrades,
    getVerificationResult,
    isVerificationInProgress,
    clearVerificationResults,
    verificationResults,
    isVerifying
  };
};

// Helper function to determine verification status based on confidence and flags
const determineVerificationStatus = (
  confidence: number,
  flaggedReasons: string[]
): VerificationStatus => {
  if (flaggedReasons.length > 0) {
    // Check if any flagged reason indicates fabrication
    const fabricationFlags = ['fabricated', 'forged', 'tampered', 'fake'];
    const hasFabricationFlag = flaggedReasons.some(reason =>
      fabricationFlags.some(flag => reason.toLowerCase().includes(flag))
    );
    
    if (hasFabricationFlag) {
      return VerificationStatus.FAILED;
    } else {
      return VerificationStatus.NEEDS_ADMIN_REVIEW;
    }
  }
  
  if (confidence >= CONFIDENCE_THRESHOLDS.DOCUMENT_FORMAT) {
    return VerificationStatus.VERIFIED;
  } else if (confidence >= 80) {
    return VerificationStatus.NEEDS_ADMIN_REVIEW;
  } else {
    return VerificationStatus.FAILED;
  }
};

// Helper function for grade verification status
const determineGradeVerificationStatus = (gradeResponse: {
  confidence: number;
  isFabricated: boolean;
  suspiciousGrades: string[];
  flaggedReasons: string[];
}): VerificationStatus => {
  if (gradeResponse.isFabricated) {
    return VerificationStatus.FAILED;
  }
  
  if (gradeResponse.suspiciousGrades.length > 0 || gradeResponse.flaggedReasons.length > 0) {
    return VerificationStatus.NEEDS_ADMIN_REVIEW;
  }
  
  if (gradeResponse.confidence >= CONFIDENCE_THRESHOLDS.GRADE_VERIFICATION) {
    return VerificationStatus.VERIFIED;
  } else {
    return VerificationStatus.NEEDS_ADMIN_REVIEW;
  }
};