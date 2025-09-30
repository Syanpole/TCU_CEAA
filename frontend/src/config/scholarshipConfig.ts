import { ApplicationStep, StepConfiguration, VerificationRules } from '../types/scholarshipTypes';

// Verification Rules and Thresholds
export const VERIFICATION_RULES: VerificationRules = {
  minimumConfidence: 95,
  schoolIdFormat: /^[A-Z0-9]{8,12}$/, // Adjust based on your school ID format
  birthCertificateFields: ['full_name', 'birth_date', 'place_of_birth', 'parents_names'],
  enrollmentFields: ['student_name', 'student_id', 'year_level', 'program', 'semester', 'academic_year'],
  voterCertificateFields: ['full_name', 'birth_date', 'address', 'precinct_number'],
  faceMatchThreshold: 95,
  livenessThreshold: 90,
  gradeVerificationThreshold: 95,
  ageVerificationThreshold: 18 // Minimum age difference between parent and student
};

// Step Configurations
export const STEP_CONFIGURATIONS: Record<ApplicationStep, StepConfiguration> = {
  [ApplicationStep.MERIT_SELECTION]: {
    step: ApplicationStep.MERIT_SELECTION,
    title: 'Merit Application Selection',
    description: 'Choose whether you are applying for merit-based scholarship',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '1 minute',
    instructions: [
      'Select whether you are applying for merit-based scholarship or regular scholarship',
      'Merit-based scholarships require grade verification',
      'Make sure you have your grades ready if applying for merit'
    ]
  },
  
  [ApplicationStep.SCHOOL_ID]: {
    step: ApplicationStep.SCHOOL_ID,
    title: 'School ID Verification',
    description: 'Upload your official school identification card',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Take a clear photo of your school ID',
      'Ensure all text is readable and not blurred',
      'Make sure the ID is not expired',
      'AI will verify the format matches sample data'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp'],
    maxFileSize: 5 * 1024 * 1024 // 5MB
  },
  
  [ApplicationStep.BIRTH_CERTIFICATE]: {
    step: ApplicationStep.BIRTH_CERTIFICATE,
    title: 'Birth Certificate Verification',
    description: 'Upload your official birth certificate (NSO/PSA copy)',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Upload a clear scan or photo of your birth certificate',
      'Must be an official NSO/PSA copy',
      'Ensure all text is clearly visible',
      'Name must match the school ID with 85% confidence',
      'Format must match sample birth certificate data'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'],
    maxFileSize: 10 * 1024 * 1024 // 10MB
  },
  
  [ApplicationStep.ENROLLMENT_CERTIFICATE]: {
    step: ApplicationStep.ENROLLMENT_CERTIFICATE,
    title: 'Certificate of Enrollment',
    description: 'Upload your certificate of enrollment for current semester',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Upload your current certificate of enrollment',
      'Document must be from the current academic year',
      'Year level must match what you inputted during registration',
      'Must include student name, ID, and year level',
      'AI will verify year level matches your input'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'],
    maxFileSize: 10 * 1024 * 1024 // 10MB
  },
  
  [ApplicationStep.VOTER_CERTIFICATE_STUDENT]: {
    step: ApplicationStep.VOTER_CERTIFICATE_STUDENT,
    title: 'Student Voter Certificate',
    description: 'Upload your voter registration certificate',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Upload your voter registration certificate',
      'Must be official COMELEC format',
      'Name must match school ID and birth certificate',
      'Address and precinct information must be visible',
      'AI will verify format and name matching'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'],
    maxFileSize: 10 * 1024 * 1024 // 10MB
  },
  
  [ApplicationStep.VOTER_CERTIFICATE_PARENT]: {
    step: ApplicationStep.VOTER_CERTIFICATE_PARENT,
    title: 'Parent/Guardian Voter Certificate',
    description: 'Upload your parent/guardian voter registration certificate',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Upload your parent or legal guardian voter registration certificate',
      'Must be official COMELEC format',
      'Birth date must show guardian is older than student',
      'Full name and address must be clearly visible',
      'AI will verify age and format requirements'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'],
    maxFileSize: 10 * 1024 * 1024 // 10MB
  },
  
  [ApplicationStep.FACE_VERIFICATION]: {
    step: ApplicationStep.FACE_VERIFICATION,
    title: 'Face Verification',
    description: 'Complete facial recognition with liveness detection',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '3 minutes',
    instructions: [
      'Position your face clearly in the camera frame',
      'Ensure good lighting and remove sunglasses/hat',
      'Follow the liveness detection prompts (blink, turn head)',
      'Face will be matched against your school ID photo',
      'Liveness detection prevents fraud using photos or videos'
    ]
  },
  
  [ApplicationStep.PHOTO_WITH_ID]: {
    step: ApplicationStep.PHOTO_WITH_ID,
    title: 'Photo Holding ID',
    description: 'Take a photo of yourself holding your school ID',
    isRequired: true,
    dependsOnMerit: false,
    estimatedTime: '2 minutes',
    instructions: [
      'Hold your school ID next to your face',
      'Ensure both your face and ID are clearly visible',
      'Make sure ID information is readable',
      'Use good lighting and stable hands',
      'AI will match your face with the ID photo and verify liveness'
    ],
    acceptedFormats: ['image/jpeg', 'image/png', 'image/webp'],
    maxFileSize: 5 * 1024 * 1024 // 5MB
  },
  
  [ApplicationStep.GRADE_SUBMISSION]: {
    step: ApplicationStep.GRADE_SUBMISSION,
    title: 'Grade Verification (Merit Only)',
    description: 'Submit your grades for GWA calculation and verification',
    isRequired: false,
    dependsOnMerit: true,
    estimatedTime: '5 minutes',
    instructions: [
      'Enter all your grades for the specified semester',
      'Include subject name, grade, and units',
      'Grades will be verified against official records',
      'AI will calculate your GWA and check for fabricated grades',
      'Merit scholarship requires minimum GWA threshold'
    ]
  },
  
  [ApplicationStep.WAITING_CONFIRMATION]: {
    step: ApplicationStep.WAITING_CONFIRMATION,
    title: 'Waiting for Confirmation',
    description: 'Your application is being reviewed by administrators',
    isRequired: false,
    dependsOnMerit: false,
    estimatedTime: '1-3 business days',
    instructions: [
      'All documents have been submitted and verified',
      'Your application is now under administrative review',
      'You will be notified via email of the final decision',
      'Check your application status regularly for updates'
    ]
  },
  
  [ApplicationStep.COMPLETED]: {
    step: ApplicationStep.COMPLETED,
    title: 'Application Completed',
    description: 'Your scholarship application has been processed',
    isRequired: false,
    dependsOnMerit: false,
    estimatedTime: 'Complete',
    instructions: [
      'Your application has been reviewed and decided',
      'Check your email for official notification',
      'If approved, follow instructions for scholarship claim',
      'If rejected, you may appeal or apply in the next cycle'
    ]
  }
};

// Application Flow Configuration
export const APPLICATION_FLOW = {
  REGULAR_FLOW: [
    ApplicationStep.MERIT_SELECTION,
    ApplicationStep.SCHOOL_ID,
    ApplicationStep.BIRTH_CERTIFICATE,
    ApplicationStep.ENROLLMENT_CERTIFICATE,
    ApplicationStep.VOTER_CERTIFICATE_STUDENT,
    ApplicationStep.VOTER_CERTIFICATE_PARENT,
    ApplicationStep.FACE_VERIFICATION,
    ApplicationStep.PHOTO_WITH_ID,
    ApplicationStep.WAITING_CONFIRMATION,
    ApplicationStep.COMPLETED
  ],
  
  MERIT_FLOW: [
    ApplicationStep.MERIT_SELECTION,
    ApplicationStep.SCHOOL_ID,
    ApplicationStep.BIRTH_CERTIFICATE,
    ApplicationStep.ENROLLMENT_CERTIFICATE,
    ApplicationStep.VOTER_CERTIFICATE_STUDENT,
    ApplicationStep.VOTER_CERTIFICATE_PARENT,
    ApplicationStep.FACE_VERIFICATION,
    ApplicationStep.PHOTO_WITH_ID,
    ApplicationStep.GRADE_SUBMISSION,
    ApplicationStep.WAITING_CONFIRMATION,
    ApplicationStep.COMPLETED
  ]
};

// Document Type Mappings
export const DOCUMENT_TYPES = {
  SCHOOL_ID: 'school_id',
  BIRTH_CERTIFICATE: 'birth_certificate',
  ENROLLMENT_CERTIFICATE: 'enrollment_certificate',
  VOTER_CERTIFICATE_STUDENT: 'voter_certificate_student',
  VOTER_CERTIFICATE_PARENT: 'voter_certificate_parent',
  FACE_VERIFICATION: 'face_verification',
  PHOTO_WITH_ID: 'photo_with_id',
  GRADES: 'grades'
} as const;

// Confidence Thresholds for Different Verification Types
export const CONFIDENCE_THRESHOLDS = {
  DOCUMENT_FORMAT: 95,
  NAME_MATCHING: 85,
  FACE_MATCHING: 95,
  LIVENESS_DETECTION: 90,
  GRADE_VERIFICATION: 95,
  AGE_VERIFICATION: 100, // Must be exact for parent age check
  OVERALL_APPLICATION: 95
};

// File Upload Constraints
export const FILE_CONSTRAINTS = {
  MAX_SIZE: {
    IMAGE: 5 * 1024 * 1024, // 5MB
    PDF: 10 * 1024 * 1024   // 10MB
  },
  ACCEPTED_FORMATS: {
    IMAGE: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
    DOCUMENT: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/pdf']
  }
};

// UI Configuration
export const UI_CONFIG = {
  CAMERA: {
    WIDTH: 640,
    HEIGHT: 480,
    FRAME_RATE: 30,
    FACING_MODE: 'user' as const
  },
  
  PROGRESS: {
    ANIMATION_DURATION: 300,
    UPDATE_INTERVAL: 100
  },
  
  NOTIFICATIONS: {
    AUTO_DISMISS_TIME: 5000,
    MAX_NOTIFICATIONS: 3
  }
};

// API Endpoints
export const API_ENDPOINTS = {
  SCHOLARSHIP_APPLICATION: '/api/scholarship/applications',
  DOCUMENT_UPLOAD: '/api/scholarship/documents',
  AI_VERIFICATION: '/api/ai/verify',
  FACE_VERIFICATION: '/api/ai/face-verify',
  GRADE_VERIFICATION: '/api/ai/grade-verify',
  ADMIN_REVIEW: '/api/admin/review'
};

// Error Messages
export const ERROR_MESSAGES = {
  FILE_TOO_LARGE: 'File size exceeds maximum limit',
  INVALID_FILE_TYPE: 'Invalid file type. Please upload accepted formats only',
  VERIFICATION_FAILED: 'Document verification failed. Please check and resubmit',
  NETWORK_ERROR: 'Network error. Please check your connection and try again',
  AI_SERVICE_ERROR: 'AI verification service is currently unavailable',
  CAMERA_ACCESS_DENIED: 'Camera access denied. Please enable camera permissions',
  FACE_NOT_DETECTED: 'Face not detected. Please position your face clearly in the frame',
  LIVENESS_CHECK_FAILED: 'Liveness check failed. Please follow the instructions carefully',
  GRADE_CALCULATION_ERROR: 'Error calculating GWA. Please check your grade entries',
  SUBMISSION_ERROR: 'Error submitting application. Please try again'
};

// Success Messages
export const SUCCESS_MESSAGES = {
  DOCUMENT_UPLOADED: 'Document uploaded successfully',
  VERIFICATION_PASSED: 'Verification completed successfully',
  STEP_COMPLETED: 'Step completed successfully',
  APPLICATION_SUBMITTED: 'Application submitted successfully',
  FACE_VERIFIED: 'Face verification completed successfully',
  GRADES_VERIFIED: 'Grades verified and GWA calculated successfully'
};

// GWA Calculation
export const GWA_CONFIG = {
  PASSING_GRADE: 75,
  MERIT_THRESHOLD: 85,
  DEAN_LIST_THRESHOLD: 90,
  GRADE_SCALE: {
    MIN: 65,
    MAX: 100
  }
};