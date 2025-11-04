import React, { useState } from 'react';
import './BasicQualification.css';

interface BasicQualificationProps {
  onComplete: (data: QualificationData) => void;
  onCancel: () => void;
}

export interface QualificationData {
  is_enrolled: boolean | null;
  is_resident: boolean | null;
  is_eighteen_or_older: boolean | null;
  is_registered_voter: boolean | null;
  parent_is_voter: boolean | null;
  has_good_moral_character: boolean | null;
  is_committed: boolean | null;
  applicant_type: 'new' | 'renewing' | '';
}

const BasicQualification: React.FC<BasicQualificationProps> = ({ onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [showReview, setShowReview] = useState(false);
  const totalSteps = 8;

  const [formData, setFormData] = useState<QualificationData>({
    is_enrolled: null as any,
    is_resident: null as any,
    is_eighteen_or_older: null as any,
    is_registered_voter: null as any,
    parent_is_voter: null as any,
    has_good_moral_character: null as any,
    is_committed: null as any,
    applicant_type: '' as any
  });

  const stepLabels = [
    'Enrollment',
    'Residency',
    'Age',
    'Voter Registration',
    'Family Voter',
    'Good Moral Character',
    'Commitment',
    'Applicant Type'
  ];

  const questions = [
    {
      field: 'is_enrolled' as keyof QualificationData,
      question: 'Are you currently enrolled at Taguig City University?',
    },
    {
      field: 'is_resident' as keyof QualificationData,
      question: 'Are you a bona fide resident of Taguig City for at least three (3) years immediately preceding the application?',
    },
    {
      field: 'is_eighteen_or_older' as keyof QualificationData,
      question: 'Are you eighteen (18) years old or older?',
    },
    {
      field: 'is_registered_voter' as keyof QualificationData,
      question: 'Are you a registered voter of the City?',
    },
    {
      field: 'parent_is_voter' as keyof QualificationData,
      question: 'Is one of your parents an active voter of Taguig City?',
    },
    {
      field: 'has_good_moral_character' as keyof QualificationData,
      question: 'Do you possess good moral character both in paper and in deeds?',
    },
    {
      field: 'is_committed' as keyof QualificationData,
      question: 'Are you committed to love and serve Taguig City?',
    }
  ];

  const handleAnswer = (value: boolean | string) => {
    const currentQuestion = questions[currentStep - 1];
    
    if (currentStep === totalSteps) {
      // Last step: applicant type
      setFormData(prev => ({ ...prev, applicant_type: value as 'new' | 'renewing' }));
    } else {
      setFormData(prev => ({ ...prev, [currentQuestion.field]: value }));
    }
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      // Show review page instead of submitting immediately
      setShowReview(true);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      onCancel();
    }
  };

  const handleClear = () => {
    if (currentStep === totalSteps) {
      setFormData(prev => ({ ...prev, applicant_type: '' as any }));
    } else {
      const currentQuestion = questions[currentStep - 1];
      setFormData(prev => ({ ...prev, [currentQuestion.field]: null as any }));
    }
  };

  const isAnswered = () => {
    if (currentStep === totalSteps) {
      return formData.applicant_type !== '' && formData.applicant_type !== null;
    }
    const currentQuestion = questions[currentStep - 1];
    return formData[currentQuestion.field] !== null && formData[currentQuestion.field] !== undefined;
  };

  const renderQuestion = () => {
    if (currentStep === totalSteps) {
      // Applicant Type step
      return (
        <div className="question-content">
          <h3 className="question-text">Are you a new or renewing applicant?</h3>
          <div className="options-container">
            <button
              className={`option-button ${formData.applicant_type === 'new' ? 'selected' : ''}`}
              onClick={() => handleAnswer('new')}
            >
              <div className="option-label">NEW</div>
              <div className="option-description">Those who are first time to apply or those who previously applied but did not qualify.</div>
            </button>
            <button
              className={`option-button ${formData.applicant_type === 'renewing' ? 'selected' : ''}`}
              onClick={() => handleAnswer('renewing')}
            >
              <div className="option-label">RENEWING</div>
            </button>
          </div>
        </div>
      );
    }

    const currentQuestion = questions[currentStep - 1];
    const currentValue = formData[currentQuestion.field];

    return (
      <div className="question-content">
        <h3 className="question-text">{currentQuestion.question}</h3>
        <div className="options-container">
          <button
            className={`option-button ${currentValue === true ? 'selected' : ''}`}
            onClick={() => handleAnswer(true)}
          >
            Yes
          </button>
          <button
            className={`option-button ${currentValue === false ? 'selected' : ''}`}
            onClick={() => handleAnswer(false)}
          >
            No
          </button>
        </div>
      </div>
    );
  };

  const renderReviewPage = () => {
    return (
      <div className="review-page">
        <div className="review-header">
          <h2>Review your answers</h2>
          <button className="review-close" onClick={() => setShowReview(false)} title="Close review">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="review-content">
          <div className="review-table">
            <div className="review-row review-header-row">
              <div className="review-cell">Question</div>
              <div className="review-cell">Answer</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[0].question}</div>
              <div className="review-cell review-answer">{formData.is_enrolled ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[1].question}</div>
              <div className="review-cell review-answer">{formData.is_resident ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[2].question}</div>
              <div className="review-cell review-answer">{formData.is_eighteen_or_older ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[3].question}</div>
              <div className="review-cell review-answer">{formData.is_registered_voter ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[4].question}</div>
              <div className="review-cell review-answer">{formData.parent_is_voter ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[5].question}</div>
              <div className="review-cell review-answer">{formData.has_good_moral_character ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">{questions[6].question}</div>
              <div className="review-cell review-answer">{formData.is_committed ? 'Yes' : 'No'}</div>
            </div>

            <div className="review-row">
              <div className="review-cell">Are you a new or renewing applicant?</div>
              <div className="review-cell review-answer">{formData.applicant_type.toUpperCase()}</div>
            </div>
          </div>

          <button className="btn-submit-final" onClick={() => onComplete(formData)}>
            Submit
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="basic-qualification-overlay">
      <div className="basic-qualification-container">
        {/* Header */}
        <div className="qualification-header">
          <div className="header-content">
            <h1 className="header-title">Basic Qualification</h1>
            <button className="home-button" onClick={onCancel} title="Close">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>

        {/* Banner */}
        <div className="qualification-banner">
          <div className="banner-overlay">
            <h2 className="banner-title">Basic Qualification Criteria</h2>
            <p className="banner-subtitle">TCU-CEAA ONLINE APPLICATION - 1ST SEMESTER - S.Y 2025-2026</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="qualification-content">
          {showReview ? (
            renderReviewPage()
          ) : (
            <div className="content-card">
              {/* Progress */}
              <div className="progress-section">
                <div className="step-info">
                  <span className="step-label">Step {currentStep} of {totalSteps}</span>
                  <span className="step-name">{stepLabels[currentStep - 1]}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Question */}
              {renderQuestion()}

              {/* Action Buttons */}
              <div className="action-buttons">
                <button className="btn-back" onClick={handleBack}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M19 12H5M12 19l-7-7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  Back
                </button>
                <div className="right-buttons">
                  <button className="btn-clear" onClick={handleClear}>
                    Clear
                  </button>
                  <button 
                    className="btn-next" 
                    onClick={handleNext}
                    disabled={!isAnswered()}
                  >
                    {currentStep === totalSteps ? 'Next' : 'Next'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BasicQualification;
