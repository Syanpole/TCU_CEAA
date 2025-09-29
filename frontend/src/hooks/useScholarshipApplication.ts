import { useState, useCallback, useEffect } from 'react';
import { 
  ScholarshipApplication, 
  ApplicationStep, 
  ApplicationStatus, 
  StepStatus, 
  ApplicationUIState,
  DocumentSubmissions,
  VerificationResults
} from '../types/scholarshipTypes';
import { APPLICATION_FLOW, STEP_CONFIGURATIONS } from '../config/scholarshipConfig';

export const useScholarshipApplication = () => {
  const [application, setApplication] = useState<ScholarshipApplication | null>(null);
  const [uiState, setUIState] = useState<ApplicationUIState>({
    currentStep: ApplicationStep.MERIT_SELECTION,
    isLoading: false,
    progress: 0,
    canProceedToNext: false,
    stepStatus: {
      [ApplicationStep.MERIT_SELECTION]: StepStatus.INCOMPLETE,
      [ApplicationStep.SCHOOL_ID]: StepStatus.INCOMPLETE,
      [ApplicationStep.BIRTH_CERTIFICATE]: StepStatus.INCOMPLETE,
      [ApplicationStep.ENROLLMENT_CERTIFICATE]: StepStatus.INCOMPLETE,
      [ApplicationStep.VOTER_CERTIFICATE_STUDENT]: StepStatus.INCOMPLETE,
      [ApplicationStep.VOTER_CERTIFICATE_PARENT]: StepStatus.INCOMPLETE,
      [ApplicationStep.FACE_VERIFICATION]: StepStatus.INCOMPLETE,
      [ApplicationStep.PHOTO_WITH_ID]: StepStatus.INCOMPLETE,
      [ApplicationStep.GRADE_SUBMISSION]: StepStatus.INCOMPLETE,
      [ApplicationStep.WAITING_CONFIRMATION]: StepStatus.INCOMPLETE,
      [ApplicationStep.COMPLETED]: StepStatus.INCOMPLETE
    }
  });

  // Initialize or load existing application
  const initializeApplication = useCallback((studentInfo: {
    studentId: string;
    studentName: string;
  }) => {
    const newApplication: ScholarshipApplication = {
      studentId: studentInfo.studentId,
      studentName: studentInfo.studentName,
      isApplyingForMerit: false,
      currentStep: ApplicationStep.MERIT_SELECTION,
      status: ApplicationStatus.DRAFT,
      submissions: {},
      verificationResults: {}
    };
    
    setApplication(newApplication);
  }, []);

  // Get application flow based on merit selection
  const getApplicationFlow = useCallback(() => {
    if (!application) return APPLICATION_FLOW.REGULAR_FLOW;
    return application.isApplyingForMerit 
      ? APPLICATION_FLOW.MERIT_FLOW 
      : APPLICATION_FLOW.REGULAR_FLOW;
  }, [application]);

  // Calculate progress percentage
  const calculateProgress = useCallback(() => {
    const flow = getApplicationFlow();
    const completedSteps = flow.filter(step => 
      uiState.stepStatus[step] === StepStatus.COMPLETED
    ).length;
    return Math.round((completedSteps / flow.length) * 100);
  }, [getApplicationFlow, uiState.stepStatus]);

  // Check if current step is complete
  const isCurrentStepComplete = useCallback(() => {
    if (!application) return false;
    return uiState.stepStatus[application.currentStep] === StepStatus.COMPLETED;
  }, [application, uiState.stepStatus]);

  // Check if can proceed to next step
  const canProceedToNext = useCallback(() => {
    if (!application) return false;
    const currentStepStatus = uiState.stepStatus[application.currentStep];
    return currentStepStatus === StepStatus.COMPLETED;
  }, [application, uiState.stepStatus]);

  // Get next step in the flow
  const getNextStep = useCallback(() => {
    if (!application) return null;
    const flow = getApplicationFlow();
    const currentIndex = flow.indexOf(application.currentStep);
    return currentIndex < flow.length - 1 ? flow[currentIndex + 1] : null;
  }, [application, getApplicationFlow]);

  // Get previous step in the flow
  const getPreviousStep = useCallback(() => {
    if (!application) return null;
    const flow = getApplicationFlow();
    const currentIndex = flow.indexOf(application.currentStep);
    return currentIndex > 0 ? flow[currentIndex - 1] : null;
  }, [application, getApplicationFlow]);

  // Update merit selection
  const updateMeritSelection = useCallback((isApplyingForMerit: boolean) => {
    if (!application) return;
    
    const updatedApplication = {
      ...application,
      isApplyingForMerit
    };
    
    setApplication(updatedApplication);
    setUIState(prev => ({
      ...prev,
      stepStatus: {
        ...prev.stepStatus,
        [ApplicationStep.MERIT_SELECTION]: StepStatus.COMPLETED
      }
    }));
  }, [application]);

  // Update step status
  const updateStepStatus = useCallback((step: ApplicationStep, status: StepStatus) => {
    setUIState(prev => ({
      ...prev,
      stepStatus: {
        ...prev.stepStatus,
        [step]: status
      }
    }));
  }, []);

  // Move to next step
  const proceedToNextStep = useCallback(() => {
    const nextStep = getNextStep();
    if (!nextStep || !application) return false;

    const updatedApplication = {
      ...application,
      currentStep: nextStep
    };

    setApplication(updatedApplication);
    setUIState(prev => ({
      ...prev,
      currentStep: nextStep
    }));

    return true;
  }, [application, getNextStep]);

  // Move to previous step
  const goToPreviousStep = useCallback(() => {
    const prevStep = getPreviousStep();
    if (!prevStep || !application) return false;

    const updatedApplication = {
      ...application,
      currentStep: prevStep
    };

    setApplication(updatedApplication);
    setUIState(prev => ({
      ...prev,
      currentStep: prevStep
    }));

    return true;
  }, [application, getPreviousStep]);

  // Jump to specific step (if allowed)
  const jumpToStep = useCallback((step: ApplicationStep) => {
    if (!application) return false;
    
    const flow = getApplicationFlow();
    const targetIndex = flow.indexOf(step);
    const currentIndex = flow.indexOf(application.currentStep);
    
    // Only allow jumping to previous steps or next immediate step if current is complete
    if (targetIndex <= currentIndex || 
        (targetIndex === currentIndex + 1 && isCurrentStepComplete())) {
      
      const updatedApplication = {
        ...application,
        currentStep: step
      };

      setApplication(updatedApplication);
      setUIState(prev => ({
        ...prev,
        currentStep: step
      }));

      return true;
    }
    
    return false;
  }, [application, getApplicationFlow, isCurrentStepComplete]);

  // Update document submission
  const updateDocumentSubmission = useCallback((
    documentType: keyof DocumentSubmissions,
    submission: any
  ) => {
    if (!application) return;

    const updatedSubmissions = {
      ...application.submissions,
      [documentType]: submission
    };

    const updatedApplication = {
      ...application,
      submissions: updatedSubmissions
    };

    setApplication(updatedApplication);
  }, [application]);

  // Update verification result
  const updateVerificationResult = useCallback((
    verificationType: keyof VerificationResults,
    result: any
  ) => {
    if (!application) return;

    const updatedResults = {
      ...application.verificationResults,
      [verificationType]: result
    };

    const updatedApplication = {
      ...application,
      verificationResults: updatedResults
    };

    setApplication(updatedApplication);
  }, [application]);

  // Set loading state
  const setLoading = useCallback((isLoading: boolean) => {
    setUIState(prev => ({
      ...prev,
      isLoading
    }));
  }, []);

  // Set error state
  const setError = useCallback((error: string | undefined) => {
    setUIState(prev => ({
      ...prev,
      error
    }));
  }, []);

  // Get current step configuration
  const getCurrentStepConfig = useCallback(() => {
    if (!application) return null;
    return STEP_CONFIGURATIONS[application.currentStep];
  }, [application]);

  // Check if step is required for current application type
  const isStepRequired = useCallback((step: ApplicationStep) => {
    const config = STEP_CONFIGURATIONS[step];
    if (config.dependsOnMerit && application) {
      return application.isApplyingForMerit;
    }
    return config.isRequired;
  }, [application]);

  // Get completed steps count
  const getCompletedStepsCount = useCallback(() => {
    const flow = getApplicationFlow();
    return flow.filter(step => 
      uiState.stepStatus[step] === StepStatus.COMPLETED
    ).length;
  }, [getApplicationFlow, uiState.stepStatus]);

  // Get total steps count
  const getTotalStepsCount = useCallback(() => {
    return getApplicationFlow().length;
  }, [getApplicationFlow]);

  // Check if application is complete
  const isApplicationComplete = useCallback(() => {
    if (!application) return false;
    return application.currentStep === ApplicationStep.COMPLETED &&
           uiState.stepStatus[ApplicationStep.COMPLETED] === StepStatus.COMPLETED;
  }, [application, uiState.stepStatus]);

  // Submit application
  const submitApplication = useCallback(() => {
    if (!application || !isCurrentStepComplete()) return false;

    const updatedApplication = {
      ...application,
      status: ApplicationStatus.UNDER_REVIEW,
      submittedAt: new Date().toISOString()
    };

    setApplication(updatedApplication);
    return true;
  }, [application, isCurrentStepComplete]);

  // Update progress whenever step status changes
  useEffect(() => {
    const progress = calculateProgress();
    const canProceed = canProceedToNext();
    
    setUIState(prev => ({
      ...prev,
      progress,
      canProceedToNext: canProceed
    }));
  }, [calculateProgress, canProceedToNext]);

  return {
    application,
    uiState,
    
    // Actions
    initializeApplication,
    updateMeritSelection,
    updateStepStatus,
    proceedToNextStep,
    goToPreviousStep,
    jumpToStep,
    updateDocumentSubmission,
    updateVerificationResult,
    setLoading,
    setError,
    submitApplication,
    
    // Getters
    getApplicationFlow,
    getCurrentStepConfig,
    getNextStep,
    getPreviousStep,
    isStepRequired,
    isCurrentStepComplete,
    canProceedToNext: canProceedToNext(),
    getCompletedStepsCount,
    getTotalStepsCount,
    isApplicationComplete,
    
    // Computed values
    progress: uiState.progress,
    currentStep: application?.currentStep || ApplicationStep.MERIT_SELECTION,
    isLoading: uiState.isLoading,
    error: uiState.error
  };
};