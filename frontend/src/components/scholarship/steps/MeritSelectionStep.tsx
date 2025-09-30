import React, { useState } from 'react';
import { ScholarshipApplication } from '../../../types/scholarshipTypes';
import { useScholarshipApplication } from '../../../hooks/useScholarshipApplication';
import './MeritSelectionStep.css';

interface MeritSelectionStepProps {
  application: ScholarshipApplication;
  onComplete: () => void;
}

const MeritSelectionStep: React.FC<MeritSelectionStepProps> = ({
  application,
  onComplete
}) => {
  const { updateMeritSelection } = useScholarshipApplication();
  const [selectedOption, setSelectedOption] = useState<boolean | null>(
    application.isApplyingForMerit ?? null
  );
  const [showDetails, setShowDetails] = useState(false);

  const handleSelection = (isApplyingForMerit: boolean) => {
    setSelectedOption(isApplyingForMerit);
  };

  const handleContinue = () => {
    if (selectedOption !== null) {
      updateMeritSelection(selectedOption);
      onComplete();
    }
  };

  return (
    <div className="merit-selection-step">
      <div className="step-content">
        <div className="selection-header">
          <h3>Choose Your Scholarship Type</h3>
          <p>Please select which type of scholarship you would like to apply for:</p>
        </div>

        <div className="selection-options">
          {/* Merit-Based Option */}
          <div 
            className={`selection-option ${selectedOption === true ? 'selected' : ''}`}
            onClick={() => handleSelection(true)}
          >
            <div className="option-header">
              <div className="option-radio">
                <input
                  id="merit-scholarship"
                  type="radio"
                  name="scholarship-type"
                  checked={selectedOption === true}
                  onChange={() => handleSelection(true)}
                  aria-label="Merit-Based Scholarship - For students with excellent academic performance"
                />
                <span className="radio-custom"></span>
              </div>
              <div className="option-content">
                <h4>Merit-Based Scholarship</h4>
                <p>For students with excellent academic performance</p>
              </div>
              <div className="option-badge merit">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
                Merit
              </div>
            </div>
            
            <div className="option-details">
              <div className="requirements">
                <h5>Requirements:</h5>
                <ul>
                  <li>Minimum GWA of 85% (1.75)</li>
                  <li>Grade verification required</li>
                  <li>No failing grades in the current semester</li>
                  <li>Academic excellence track record</li>
                </ul>
              </div>
              
              <div className="benefits">
                <h5>Benefits:</h5>
                <ul>
                  <li>Higher scholarship amount</li>
                  <li>Priority processing</li>
                  <li>Academic recognition</li>
                  <li>Renewable for next semester</li>
                </ul>
              </div>
              
              <div className="additional-steps">
                <h5>Additional Steps Required:</h5>
                <ul>
                  <li>Grade submission and verification</li>
                  <li>GWA calculation by AI system</li>
                  <li>Academic record validation</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Regular Scholarship Option */}
          <div 
            className={`selection-option ${selectedOption === false ? 'selected' : ''}`}
            onClick={() => handleSelection(false)}
          >
            <div className="option-header">
              <div className="option-radio">
                <input
                  id="regular-scholarship"
                  type="radio"
                  name="scholarship-type"
                  checked={selectedOption === false}
                  onChange={() => handleSelection(false)}
                  aria-label="Regular Scholarship - Standard financial assistance for qualified students"
                />
                <span className="radio-custom"></span>
              </div>
              <div className="option-content">
                <h4>Regular Scholarship</h4>
                <p>Standard financial assistance for qualified students</p>
              </div>
              <div className="option-badge regular">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                </svg>
                Regular
              </div>
            </div>
            
            <div className="option-details">
              <div className="requirements">
                <h5>Requirements:</h5>
                <ul>
                  <li>Currently enrolled student</li>
                  <li>Valid student ID and documents</li>
                  <li>Financial need demonstration</li>
                  <li>Good moral standing</li>
                </ul>
              </div>
              
              <div className="benefits">
                <h5>Benefits:</h5>
                <ul>
                  <li>Financial assistance for tuition</li>
                  <li>Standard processing timeline</li>
                  <li>Basic scholarship coverage</li>
                  <li>Support for educational expenses</li>
                </ul>
              </div>
              
              <div className="additional-steps">
                <h5>Steps Required:</h5>
                <ul>
                  <li>Document verification only</li>
                  <li>Identity confirmation</li>
                  <li>Eligibility check</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Information Section */}
        <div className="information-section">
          <button 
            className="info-toggle" 
            onClick={() => setShowDetails(!showDetails)}
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Important Information
            <svg 
              viewBox="0 0 24 24" 
              fill="currentColor"
              className={`chevron ${showDetails ? 'expanded' : ''}`}
            >
              <path d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showDetails && (
            <div className="info-details">
              <div className="info-grid">
                <div className="info-item">
                  <h5>Processing Time</h5>
                  <p>Merit applications take 3-5 business days for grade verification. Regular applications process in 1-2 business days.</p>
                </div>
                
                <div className="info-item">
                  <h5>AI Verification</h5>
                  <p>All documents undergo 95% confidence AI verification. Suspicious documents are flagged for manual review.</p>
                </div>
                
                <div className="info-item">
                  <h5>Grade Requirements</h5>
                  <p>Merit applicants must maintain minimum 1.75 GWA. Fabricated grades will result in automatic rejection.</p>
                </div>
                
                <div className="info-item">
                  <h5>Document Security</h5>
                  <p>All uploaded documents are encrypted and stored securely. Face verification prevents identity fraud.</p>
                </div>
              </div>
              
              <div className="warning-notice">
                <div className="warning-icon">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="warning-content">
                  <h6>Important Notice</h6>
                  <p>Submitting false information or fabricated documents will result in permanent disqualification from all scholarship programs. Our AI system has 95% accuracy in detecting fraudulent documents.</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Selection Summary */}
        {selectedOption !== null && (
          <div className="selection-summary">
            <div className="summary-header">
              <h4>Your Selection</h4>
            </div>
            <div className="summary-content">
              <div className="selected-type">
                <div className={`type-badge ${selectedOption ? 'merit' : 'regular'}`}>
                  {selectedOption ? (
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                    </svg>
                  )}
                  {selectedOption ? 'Merit-Based Scholarship' : 'Regular Scholarship'}
                </div>
              </div>
              
              <div className="next-steps">
                <h5>Next Steps:</h5>
                <ul>
                  <li>Upload your school ID for verification</li>
                  <li>Submit birth certificate and enrollment documents</li>
                  <li>Complete voter certificate verification (student and parent)</li>
                  <li>Undergo face verification with liveness detection</li>
                  <li>Take photo holding your ID</li>
                  {selectedOption && <li>Submit and verify your grades for GWA calculation</li>}
                  <li>Wait for administrative confirmation</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Continue Button */}
        <div className="step-actions">
          <button
            className={`btn-primary continue-btn ${selectedOption === null ? 'disabled' : ''}`}
            onClick={handleContinue}
            disabled={selectedOption === null}
          >
            Continue with {selectedOption === true ? 'Merit-Based' : selectedOption === false ? 'Regular' : ''} Application
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MeritSelectionStep;