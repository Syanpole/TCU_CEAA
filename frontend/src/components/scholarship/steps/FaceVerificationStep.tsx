import React, { useState } from 'react';
import { ScholarshipApplication } from '../../../types/scholarshipTypes';
import './FaceVerificationStep.css';

interface FaceVerificationStepProps {
  application: ScholarshipApplication;
  referenceImageUrl?: string;
  onComplete: () => void;
}

const FaceVerificationStep: React.FC<FaceVerificationStepProps> = ({
  application,
  referenceImageUrl,
  onComplete
}) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationComplete, setVerificationComplete] = useState(false);

  const handleStartVerification = () => {
    setIsVerifying(true);
    // Simulate verification process
    setTimeout(() => {
      setIsVerifying(false);
      setVerificationComplete(true);
    }, 3000);
  };

  const handleContinue = () => {
    onComplete();
  };

  return (
    <div className="face-verification-step">
      <div className="verification-content">
        <div className="instructions">
          <h4>Face Verification Instructions</h4>
          <ul>
            <li>Position your face clearly in the camera frame</li>
            <li>Ensure good lighting and remove sunglasses/hat</li>
            <li>Follow the liveness detection prompts</li>
            <li>Face will be matched against your school ID photo</li>
          </ul>
        </div>

        {!verificationComplete ? (
          <div className="verification-area">
            <div className="camera-placeholder">
              <div className="camera-icon">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                  <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                </svg>
              </div>
              <h4>Face Verification Camera</h4>
              <p>Click to start face verification</p>
            </div>

            {!isVerifying ? (
              <button className="start-verification-btn" onClick={handleStartVerification}>
                Start Face Verification
              </button>
            ) : (
              <div className="verifying-status">
                <div className="verification-spinner"></div>
                <p>Performing face verification...</p>
              </div>
            )}
          </div>
        ) : (
          <div className="verification-complete">
            <div className="success-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4>Face Verification Complete</h4>
            <p>Your identity has been successfully verified</p>
            <button className="continue-btn" onClick={handleContinue}>
              Continue to Next Step
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceVerificationStep;