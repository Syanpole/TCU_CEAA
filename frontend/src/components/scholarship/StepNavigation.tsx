import React from 'react';
import { 
  ScholarshipApplication, 
  ApplicationUIState, 
  ApplicationStep 
} from '../../types/scholarshipTypes';
import { STEP_CONFIGURATIONS } from '../../config/scholarshipConfig';
import './StepNavigation.css';

interface StepNavigationProps {
  application: ScholarshipApplication;
  uiState: ApplicationUIState;
  onPrevious: () => void;
  onNext: () => void;
  canProceed: boolean;
}

const StepNavigation: React.FC<StepNavigationProps> = ({
  application,
  uiState,
  onPrevious,
  onNext,
  canProceed
}) => {
  const getApplicationFlow = () => {
    const allSteps = Object.values(ApplicationStep);
    return allSteps.filter(step => {
      const config = STEP_CONFIGURATIONS[step];
      if (config.dependsOnMerit) {
        return application.isApplyingForMerit;
      }
      return true;
    });
  };

  const getCurrentStepIndex = () => {
    const flow = getApplicationFlow();
    return flow.indexOf(application.currentStep);
  };

  const isFirstStep = () => {
    return getCurrentStepIndex() === 0;
  };

  const isLastStep = () => {
    const flow = getApplicationFlow();
    return getCurrentStepIndex() === flow.length - 1;
  };

  const getNextStepTitle = () => {
    const flow = getApplicationFlow();
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < flow.length - 1) {
      const nextStep = flow[currentIndex + 1];
      return STEP_CONFIGURATIONS[nextStep].title;
    }
    return null;
  };

  const getPreviousStepTitle = () => {
    const flow = getApplicationFlow();
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      const prevStep = flow[currentIndex - 1];
      return STEP_CONFIGURATIONS[prevStep].title;
    }
    return null;
  };

  const getNextButtonText = () => {
    if (application.currentStep === ApplicationStep.WAITING_CONFIRMATION) {
      return 'Complete Application';
    }
    if (application.currentStep === ApplicationStep.GRADE_SUBMISSION) {
      return 'Submit Application';
    }
    return 'Continue';
  };

  const getNextButtonIcon = () => {
    if (application.currentStep === ApplicationStep.WAITING_CONFIRMATION ||
        application.currentStep === ApplicationStep.GRADE_SUBMISSION) {
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    return (
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M9 5l7 7-7 7" />
      </svg>
    );
  };

  if (application.currentStep === ApplicationStep.COMPLETED) {
    return null; // No navigation needed for completed step
  }

  return (
    <div className="step-navigation">
      <div className="navigation-content">
        {/* Progress Info */}
        <div className="navigation-info">
          <div className="step-counter">
            Step {getCurrentStepIndex() + 1} of {getApplicationFlow().length}
          </div>
          <div className="progress-mini">
            <div className="progress-bar-mini">
              <div 
                className="progress-fill-mini"
                data-progress={uiState.progress}
              ></div>
            </div>
            <span className="progress-text">{uiState.progress}% Complete</span>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="navigation-buttons">
          {/* Previous Button */}
          {!isFirstStep() && (
            <button
              className="nav-btn nav-btn-secondary"
              onClick={onPrevious}
              disabled={uiState.isLoading}
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M15 19l-7-7 7-7" />
              </svg>
              <div className="btn-content">
                <span className="btn-label">Previous</span>
                {getPreviousStepTitle() && (
                  <span className="btn-subtitle">{getPreviousStepTitle()}</span>
                )}
              </div>
            </button>
          )}

          {/* Next Button */}
          {!isLastStep() && (
            <button
              className={`nav-btn nav-btn-primary ${!canProceed ? 'disabled' : ''}`}
              onClick={onNext}
              disabled={!canProceed || uiState.isLoading}
            >
              <div className="btn-content">
                <span className="btn-label">{getNextButtonText()}</span>
                {getNextStepTitle() && (
                  <span className="btn-subtitle">{getNextStepTitle()}</span>
                )}
              </div>
              {getNextButtonIcon()}
            </button>
          )}
        </div>
      </div>

      {/* Requirement Notice */}
      {!canProceed && !uiState.isLoading && (
        <div className="requirement-notice">
          <div className="notice-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="notice-content">
            <p>Please complete all requirements in this step before continuing.</p>
            {application.currentStep === ApplicationStep.MERIT_SELECTION && (
              <p>Select whether you are applying for merit-based scholarship.</p>
            )}
            {(application.currentStep === ApplicationStep.SCHOOL_ID ||
              application.currentStep === ApplicationStep.BIRTH_CERTIFICATE ||
              application.currentStep === ApplicationStep.ENROLLMENT_CERTIFICATE ||
              application.currentStep === ApplicationStep.VOTER_CERTIFICATE_STUDENT ||
              application.currentStep === ApplicationStep.VOTER_CERTIFICATE_PARENT ||
              application.currentStep === ApplicationStep.PHOTO_WITH_ID) && (
              <p>Upload and verify your document to proceed.</p>
            )}
            {application.currentStep === ApplicationStep.FACE_VERIFICATION && (
              <p>Complete face verification with liveness detection.</p>
            )}
            {application.currentStep === ApplicationStep.GRADE_SUBMISSION && (
              <p>Enter and verify all your grades for GWA calculation.</p>
            )}
          </div>
        </div>
      )}

      {/* Loading Notice */}
      {uiState.isLoading && (
        <div className="loading-notice">
          <div className="loading-spinner-small"></div>
          <span>Processing your request...</span>
        </div>
      )}

      {/* Error Notice */}
      {uiState.error && (
        <div className="error-notice">
          <div className="notice-icon error">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="notice-content">
            <p>{uiState.error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StepNavigation;