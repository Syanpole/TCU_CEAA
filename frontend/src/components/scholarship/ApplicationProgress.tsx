import React from 'react';
import { 
  ScholarshipApplication, 
  ApplicationUIState, 
  ApplicationStep,
  StepStatus 
} from '../../types/scholarshipTypes';
import { STEP_CONFIGURATIONS } from '../../config/scholarshipConfig';
import './ApplicationProgress.css';

interface ApplicationProgressProps {
  application: ScholarshipApplication;
  uiState: ApplicationUIState;
  onStepClick?: (step: ApplicationStep) => void;
}

const ApplicationProgress: React.FC<ApplicationProgressProps> = ({
  application,
  uiState,
  onStepClick
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

  const getStepNumber = (step: ApplicationStep) => {
    const flow = getApplicationFlow();
    return flow.indexOf(step) + 1;
  };

  const getStepStatusClass = (step: ApplicationStep) => {
    const status = uiState.stepStatus[step];
    const isCurrent = application.currentStep === step;
    
    let className = 'progress-step';
    
    if (isCurrent) {
      className += ' current';
    }
    
    switch (status) {
      case StepStatus.COMPLETED:
        className += ' completed';
        break;
      case StepStatus.IN_PROGRESS:
        className += ' in-progress';
        break;
      case StepStatus.ERROR:
        className += ' error';
        break;
      case StepStatus.FLAGGED:
        className += ' flagged';
        break;
      default:
        className += ' incomplete';
    }
    
    return className;
  };

  const isStepClickable = (step: ApplicationStep) => {
    const flow = getApplicationFlow();
    const stepIndex = flow.indexOf(step);
    const currentIndex = flow.indexOf(application.currentStep);
    
    // Can click on previous steps or next immediate step if current is complete
    return stepIndex <= currentIndex || 
           (stepIndex === currentIndex + 1 && 
            uiState.stepStatus[application.currentStep] === StepStatus.COMPLETED);
  };

  const handleStepClick = (step: ApplicationStep) => {
    if (onStepClick && isStepClickable(step)) {
      onStepClick(step);
    }
  };

  const getStepIcon = (step: ApplicationStep, status: StepStatus) => {
    if (status === StepStatus.COMPLETED) {
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    
    if (status === StepStatus.ERROR || status === StepStatus.FLAGGED) {
      return (
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    }
    
    if (status === StepStatus.IN_PROGRESS) {
      return (
        <div className="progress-spinner">
          <div className="spinner"></div>
        </div>
      );
    }
    
    // Default step number
    return <span>{getStepNumber(step)}</span>;
  };

  const flow = getApplicationFlow();
  const completedSteps = flow.filter(step => 
    uiState.stepStatus[step] === StepStatus.COMPLETED
  ).length;

  return (
    <div className="application-progress">
      {/* Progress Header */}
      <div className="progress-header">
        <div className="progress-info">
          <h3>Application Progress</h3>
          <p>{completedSteps} of {flow.length} steps completed</p>
        </div>
        <div className="progress-percentage">
          <span className="percentage">{uiState.progress}%</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            data-progress={uiState.progress}
          ></div>
        </div>
      </div>

      {/* Step Indicators */}
      <div className="progress-steps">
        {flow.map((step, index) => {
          const config = STEP_CONFIGURATIONS[step];
          const status = uiState.stepStatus[step];
          const isClickable = isStepClickable(step);
          
          return (
            <div key={step} className="step-wrapper">
              {/* Step Connector Line */}
              {index > 0 && (
                <div className="step-connector">
                  <div 
                    className={`connector-line ${
                      uiState.stepStatus[flow[index - 1]] === StepStatus.COMPLETED 
                        ? 'completed' 
                        : ''
                    }`}
                  ></div>
                </div>
              )}
              
              {/* Step Item */}
              <div 
                className={getStepStatusClass(step)}
                onClick={() => handleStepClick(step)}
                {...(isClickable && {
                  role: 'button',
                  tabIndex: 0,
                  'aria-label': `Go to ${config.title} step`
                })}
                onKeyDown={(e) => {
                  if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
                    e.preventDefault();
                    handleStepClick(step);
                  }
                }}
              >
                <div className="step-icon">
                  {getStepIcon(step, status)}
                </div>
                
                <div className="step-content">
                  <h4 className="step-title">{config.title}</h4>
                  <p className="step-description">{config.description}</p>
                  
                  {status === StepStatus.ERROR && (
                    <div className="step-status error">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Error - Click to retry
                    </div>
                  )}
                  
                  {status === StepStatus.FLAGGED && (
                    <div className="step-status flagged">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                      </svg>
                      Flagged for review
                    </div>
                  )}
                  
                  {status === StepStatus.IN_PROGRESS && (
                    <div className="step-status in-progress">
                      <div className="status-spinner"></div>
                      In progress...
                    </div>
                  )}
                  
                  {status === StepStatus.COMPLETED && (
                    <div className="step-status completed">
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M5 13l4 4L19 7" />
                      </svg>
                      Completed
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Mobile Progress Summary */}
      <div className="mobile-progress-summary">
        <div className="current-step">
          <h4>Current Step: {STEP_CONFIGURATIONS[application.currentStep].title}</h4>
          <p>Step {getStepNumber(application.currentStep)} of {flow.length}</p>
        </div>
        <div className="progress-circle">
          <svg viewBox="0 0 36 36" className="circular-chart">
            <path
              className="circle-bg"
              d="M18 2.0845
                 a 15.9155 15.9155 0 0 1 0 31.831
                 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="circle"
              strokeDasharray={`${uiState.progress}, 100`}
              d="M18 2.0845
                 a 15.9155 15.9155 0 0 1 0 31.831
                 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <div className="percentage">{uiState.progress}%</div>
        </div>
      </div>
    </div>
  );
};

export default ApplicationProgress;