import React, { useState, useEffect } from 'react';
import { useScholarshipApplication } from '../../hooks/useScholarshipApplication';
import { ApplicationStep } from '../../types/scholarshipTypes';
import MeritSelectionStep from './steps/MeritSelectionStep';
import DocumentUploadStep from './steps/DocumentUploadStep';
import FaceVerificationStep from './steps/FaceVerificationStep';
import GradeSubmissionStep from './steps/GradeSubmissionStep';
import WaitingConfirmationStep from './steps/WaitingConfirmationStep';
import ApplicationProgress from './ApplicationProgress';
import StepNavigation from './StepNavigation';
import './ScholarshipApplicationForm.css';

interface ScholarshipApplicationFormProps {
  studentInfo: {
    studentId: string;
    studentName: string;
    yearLevel: string;
    program: string;
  };
  onComplete?: () => void;
  onCancel?: () => void;
}

const ScholarshipApplicationForm: React.FC<ScholarshipApplicationFormProps> = ({
  studentInfo,
  onComplete,
  onCancel
}) => {
  const {
    application,
    uiState,
    initializeApplication,
    proceedToNextStep,
    goToPreviousStep,
    jumpToStep,
    getCurrentStepConfig,
    isCurrentStepComplete,
    isApplicationComplete,
    progress,
    currentStep,
    isLoading
  } = useScholarshipApplication();

  const [showExitConfirmation, setShowExitConfirmation] = useState(false);

  // Initialize application on mount
  useEffect(() => {
    initializeApplication({
      studentId: studentInfo.studentId,
      studentName: studentInfo.studentName
    });
  }, [initializeApplication, studentInfo]);

  // Handle application completion
  useEffect(() => {
    if (isApplicationComplete() && onComplete) {
      onComplete();
    }
  }, [isApplicationComplete, onComplete]);

  const handleNext = () => {
    if (proceedToNextStep()) {
      // Auto-scroll to top when moving to next step
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePrevious = () => {
    if (goToPreviousStep()) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleStepClick = (step: ApplicationStep) => {
    if (jumpToStep(step)) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleExit = () => {
    if (progress > 10) {
      setShowExitConfirmation(true);
    } else if (onCancel) {
      onCancel();
    }
  };

  const confirmExit = () => {
    setShowExitConfirmation(false);
    if (onCancel) {
      onCancel();
    }
  };

  const cancelExit = () => {
    setShowExitConfirmation(false);
  };

  const renderCurrentStep = () => {
    if (!application) return null;

    switch (currentStep) {
      case ApplicationStep.MERIT_SELECTION:
        return (
          <MeritSelectionStep
            application={application}
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.SCHOOL_ID:
        return (
          <DocumentUploadStep
            application={application}
            documentType="school_id"
            title="Upload School ID"
            description="Please upload a clear photo of your official school identification card"
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.BIRTH_CERTIFICATE:
        return (
          <DocumentUploadStep
            application={application}
            documentType="birth_certificate"
            title="Upload Birth Certificate"
            description="Please upload your official birth certificate (NSO/PSA copy)"
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.ENROLLMENT_CERTIFICATE:
        return (
          <DocumentUploadStep
            application={application}
            documentType="enrollment_certificate"
            title="Upload Certificate of Enrollment"
            description="Please upload your certificate of enrollment for the current semester"
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.VOTER_CERTIFICATE_STUDENT:
        return (
          <DocumentUploadStep
            application={application}
            documentType="voter_certificate_student"
            title="Upload Your Voter Certificate"
            description="Please upload your voter registration certificate"
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.VOTER_CERTIFICATE_PARENT:
        return (
          <DocumentUploadStep
            application={application}
            documentType="voter_certificate_parent"
            title="Upload Parent/Guardian Voter Certificate"
            description="Please upload your parent or legal guardian's voter registration certificate"
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.FACE_VERIFICATION:
        return (
          <FaceVerificationStep
            application={application}
            referenceImageUrl={application.submissions.schoolId?.fileUrl}
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.PHOTO_WITH_ID:
        return (
          <DocumentUploadStep
            application={application}
            documentType="photo_with_id"
            title="Photo Holding ID"
            description="Take a photo of yourself holding your school ID next to your face"
            isCamera={true}
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.GRADE_SUBMISSION:
        return (
          <GradeSubmissionStep
            application={application}
            studentInfo={studentInfo}
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.WAITING_CONFIRMATION:
        return (
          <WaitingConfirmationStep
            application={application}
            onComplete={() => handleNext()}
          />
        );

      case ApplicationStep.COMPLETED:
        return (
          <div className="completion-step">
            <div className="completion-content">
              <div className="completion-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2>Application Completed!</h2>
              <p>Your scholarship application has been successfully submitted and is being reviewed.</p>
              <button className="btn-primary" onClick={onComplete}>
                Return to Dashboard
              </button>
            </div>
          </div>
        );

      default:
        return <div>Unknown step</div>;
    }
  };

  const stepConfig = getCurrentStepConfig();

  if (!application || !stepConfig) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading application...</p>
      </div>
    );
  }

  return (
    <div className="scholarship-application-container">
      <div className="scholarship-application-content">
        {/* Header */}
        <div className="application-header">
          <div className="header-content">
            <h1>Scholarship Application</h1>
            <p>Complete all steps to submit your scholarship application</p>
            <div className="student-info">
              <span><strong>Student:</strong> {studentInfo.studentName}</span>
              <span><strong>ID:</strong> {studentInfo.studentId}</span>
              <span><strong>Program:</strong> {studentInfo.program}</span>
            </div>
          </div>
          <button className="exit-btn" onClick={handleExit}>
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18L18 6M6 6l12 12" />
            </svg>
            Exit
          </button>
        </div>

        {/* Progress Bar */}
        <ApplicationProgress
          application={application}
          uiState={uiState}
          onStepClick={handleStepClick}
        />

        {/* Current Step Content */}
        <div className="step-container">
          <div className="step-header">
            <div className="step-info">
              <h2>{stepConfig.title}</h2>
              <p>{stepConfig.description}</p>
              <div className="step-meta">
                <span className="estimated-time">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 6v6l4 2" />
                    <circle cx="12" cy="12" r="10" />
                  </svg>
                  Estimated time: {stepConfig.estimatedTime}
                </span>
              </div>
            </div>
          </div>

          <div className="step-content">
            {isLoading ? (
              <div className="loading-overlay">
                <div className="loading-spinner"></div>
                <p>Processing...</p>
              </div>
            ) : (
              renderCurrentStep()
            )}
          </div>
        </div>

        {/* Navigation */}
        <StepNavigation
          application={application}
          uiState={uiState}
          onPrevious={handlePrevious}
          onNext={handleNext}
          canProceed={isCurrentStepComplete()}
        />

        {/* Exit Confirmation Modal */}
        {showExitConfirmation && (
          <div className="modal-overlay">
            <div className="exit-confirmation-modal">
              <div className="modal-header">
                <h3>Exit Application</h3>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to exit your scholarship application?</p>
                <p className="warning-text">
                  Your progress will be saved, but you'll need to complete the remaining steps later.
                </p>
                <div className="progress-info">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ '--progress-width': `${progress}%` } as React.CSSProperties}
                    ></div>
                  </div>
                  <span>{progress}% completed</span>
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-secondary" onClick={cancelExit}>
                  Continue Application
                </button>
                <button className="btn-danger" onClick={confirmExit}>
                  Exit and Save Progress
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScholarshipApplicationForm;