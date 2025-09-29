// Scholarship Application Types
export interface ScholarshipApplication {
  id?: number;
  studentId: string;
  studentName: string;
  isApplyingForMerit: boolean;
  currentStep: ApplicationStep;
  status: ApplicationStatus;
  submissions: DocumentSubmissions;
  verificationResults: VerificationResults;
  gradeInfo?: GradeInformation;
  createdAt?: string;
  updatedAt?: string;
  submittedAt?: string;
}

export enum ApplicationStep {
  MERIT_SELECTION = 'merit_selection',
  SCHOOL_ID = 'school_id',
  BIRTH_CERTIFICATE = 'birth_certificate',
  ENROLLMENT_CERTIFICATE = 'enrollment_certificate',
  VOTER_CERTIFICATE_STUDENT = 'voter_certificate_student',
  VOTER_CERTIFICATE_PARENT = 'voter_certificate_parent',
  FACE_VERIFICATION = 'face_verification',
  PHOTO_WITH_ID = 'photo_with_id',
  GRADE_SUBMISSION = 'grade_submission',
  WAITING_CONFIRMATION = 'waiting_confirmation',
  COMPLETED = 'completed'
}

export enum ApplicationStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  UNDER_REVIEW = 'under_review',
  FLAGGED_FOR_REVIEW = 'flagged_for_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  COMPLETED = 'completed'
}

export interface DocumentSubmissions {
  schoolId?: DocumentSubmission;
  birthCertificate?: DocumentSubmission;
  enrollmentCertificate?: DocumentSubmission;
  voterCertificateStudent?: DocumentSubmission;
  voterCertificateParent?: DocumentSubmission;
  faceVerification?: FaceSubmission;
  photoWithId?: DocumentSubmission;
  grades?: GradeSubmission[];
}

export interface DocumentSubmission {
  id?: string;
  fileName: string;
  fileUrl?: string;
  fileData?: File;
  uploadedAt: Date;
  status: SubmissionStatus;
  aiVerification?: AIVerificationResult;
  metadata?: DocumentMetadata;
}

export interface FaceSubmission {
  id?: string;
  imageData: string; // base64 encoded
  livenessScore?: number;
  capturedAt: Date;
  status: SubmissionStatus;
  aiVerification?: AIVerificationResult;
}

export interface GradeSubmission {
  id?: string;
  subject: string;
  grade: number;
  unit: number;
  semester: string;
  yearLevel: string;
  status: SubmissionStatus;
  aiVerification?: AIVerificationResult;
}

export enum SubmissionStatus {
  PENDING = 'pending',
  VERIFYING = 'verifying',
  VERIFIED = 'verified',
  FLAGGED = 'flagged',
  REJECTED = 'rejected'
}

export interface AIVerificationResult {
  id?: string;
  confidence: number; // 0-100%
  status: VerificationStatus;
  feedback: string;
  matchingFields: MatchingField[];
  flaggedReasons: string[];
  verifiedAt: Date;
  processingTime: number; // in milliseconds
}

export enum VerificationStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  VERIFIED = 'verified',
  FLAGGED = 'flagged',
  FAILED = 'failed',
  NEEDS_ADMIN_REVIEW = 'needs_admin_review'
}

export interface MatchingField {
  field: string;
  expectedValue?: string;
  actualValue?: string;
  confidence: number;
  isMatch: boolean;
}

export interface VerificationResults {
  schoolId?: AIVerificationResult;
  birthCertificate?: AIVerificationResult;
  enrollmentCertificate?: AIVerificationResult;
  voterCertificateStudent?: AIVerificationResult;
  voterCertificateParent?: AIVerificationResult;
  faceVerification?: AIVerificationResult;
  photoWithId?: AIVerificationResult;
  grades?: AIVerificationResult;
  overallConfidence?: number;
  overallStatus?: VerificationStatus;
}

export interface DocumentMetadata {
  yearLevel?: string;
  studentName?: string;
  studentId?: string;
  birthDate?: string;
  parentName?: string;
  parentBirthDate?: string;
  semester?: string;
  academicYear?: string;
}

export interface GradeInformation {
  yearLevel: string;
  semester: string;
  academicYear: string;
  totalUnits: number;
  totalGradePoints: number;
  gwa: number; // General Weighted Average
  isEligibleForMerit: boolean;
  subjects: GradeSubmission[];
}

// Verification Rules and Thresholds
export interface VerificationRules {
  minimumConfidence: number; // 95%
  schoolIdFormat: RegExp;
  birthCertificateFields: string[];
  enrollmentFields: string[];
  voterCertificateFields: string[];
  faceMatchThreshold: number; // 95%
  livenessThreshold: number; // 90%
  gradeVerificationThreshold: number; // 95%
  ageVerificationThreshold: number; // Parent must be older than student
}

// API Response Types
export interface VerificationResponse {
  success: boolean;
  result: AIVerificationResult;
  error?: string;
}

export interface UploadResponse {
  success: boolean;
  fileUrl?: string;
  fileId?: string;
  error?: string;
}

// UI State Types
export interface ApplicationUIState {
  currentStep: ApplicationStep;
  isLoading: boolean;
  error?: string;
  progress: number; // 0-100%
  canProceedToNext: boolean;
  stepStatus: Record<ApplicationStep, StepStatus>;
}

export enum StepStatus {
  INCOMPLETE = 'incomplete',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ERROR = 'error',
  FLAGGED = 'flagged'
}

// Form Data Types
export interface MeritSelectionData {
  isApplyingForMerit: boolean;
  yearLevel: string;
  expectedGWA?: number;
}

export interface StudentBasicInfo {
  studentId: string;
  firstName: string;
  lastName: string;
  yearLevel: string;
  program: string;
  section?: string;
}

// Camera and Face Detection Types
export interface CameraSettings {
  width: number;
  height: number;
  facingMode: 'user' | 'environment';
  frameRate: number;
}

export interface LivenessDetectionResult {
  isLive: boolean;
  confidence: number;
  detectionMethods: LivenessMethod[];
}

export enum LivenessMethod {
  BLINK_DETECTION = 'blink_detection',
  HEAD_MOVEMENT = 'head_movement',
  DEPTH_ANALYSIS = 'depth_analysis',
  TEXTURE_ANALYSIS = 'texture_analysis'
}

// Admin Review Types
export interface AdminReviewItem {
  applicationId: number;
  studentName: string;
  documentType: string;
  submissionId: string;
  flaggedReasons: string[];
  confidence: number;
  submittedAt: Date;
  reviewStatus: AdminReviewStatus;
  reviewerNotes?: string;
}

export enum AdminReviewStatus {
  PENDING = 'pending',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  NEEDS_RESUBMISSION = 'needs_resubmission'
}

// Notification Types
export interface ApplicationNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  applicationId?: number;
  documentType?: string;
  timestamp: Date;
  isRead: boolean;
}

export enum NotificationType {
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  INFO = 'info',
  VERIFICATION_COMPLETE = 'verification_complete',
  ADMIN_REVIEW_REQUIRED = 'admin_review_required',
  APPLICATION_APPROVED = 'application_approved',
  APPLICATION_REJECTED = 'application_rejected'
}

// Step Configuration
export interface StepConfiguration {
  step: ApplicationStep;
  title: string;
  description: string;
  isRequired: boolean;
  dependsOnMerit: boolean;
  estimatedTime: string;
  instructions: string[];
  acceptedFormats?: string[];
  maxFileSize?: number;
}

// Error Types
export interface ApplicationError {
  code: string;
  message: string;
  field?: string;
  step?: ApplicationStep;
  details?: Record<string, any>;
}

// Progress Tracking
export interface ProgressTracker {
  totalSteps: number;
  completedSteps: number;
  currentStepIndex: number;
  estimatedTimeRemaining: string;
  stepProgress: Record<ApplicationStep, number>;
}