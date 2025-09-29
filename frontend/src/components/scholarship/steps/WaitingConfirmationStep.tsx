import React, { useState, useEffect } from 'react';
import { ScholarshipApplication } from '../../../types/scholarshipTypes';
import './WaitingConfirmationStep.css';

interface WaitingConfirmationStepProps {
  application: ScholarshipApplication;
  onComplete: () => void;
}

const WaitingConfirmationStep: React.FC<WaitingConfirmationStepProps> = ({
  application,
  onComplete
}) => {
  const [timeElapsed, setTimeElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    // Auto-complete after 10 seconds for demo
    const autoComplete = setTimeout(() => {
      onComplete();
    }, 10000);

    return () => {
      clearInterval(timer);
      clearTimeout(autoComplete);
    };
  }, [onComplete]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="waiting-confirmation-step">
      <div className="waiting-content">
        <div className="status-icon">
          <div className="loading-spinner"></div>
        </div>
        
        <h3>Application Under Review</h3>
        <p>Your scholarship application has been submitted and is currently being reviewed by our administrators.</p>

        <div className="application-summary">
          <h4>Application Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="label">Student:</span>
              <span className="value">{application.studentName}</span>
            </div>
            <div className="summary-item">
              <span className="label">Student ID:</span>
              <span className="value">{application.studentId}</span>
            </div>
            <div className="summary-item">
              <span className="label">Application Type:</span>
              <span className="value">
                {application.isApplyingForMerit ? 'Merit-Based Scholarship' : 'Regular Scholarship'}
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Submitted:</span>
              <span className="value">{new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="processing-info">
          <h4>What Happens Next?</h4>
          <div className="timeline">
            <div className="timeline-item completed">
              <div className="timeline-icon">✓</div>
              <div className="timeline-content">
                <h5>Documents Submitted</h5>
                <p>All required documents have been uploaded and AI verified</p>
              </div>
            </div>
            
            <div className="timeline-item active">
              <div className="timeline-icon">
                <div className="mini-spinner"></div>
              </div>
              <div className="timeline-content">
                <h5>Administrative Review</h5>
                <p>Administrators are reviewing your application and documents</p>
              </div>
            </div>
            
            <div className="timeline-item">
              <div className="timeline-icon">3</div>
              <div className="timeline-content">
                <h5>Final Decision</h5>
                <p>You will receive an email notification with the final decision</p>
              </div>
            </div>
          </div>
        </div>

        <div className="estimated-time">
          <h4>Estimated Processing Time</h4>
          <p>
            {application.isApplyingForMerit 
              ? '3-5 business days (Merit applications require additional verification)'
              : '1-2 business days'
            }
          </p>
        </div>

        <div className="contact-info">
          <h4>Need Help?</h4>
          <p>If you have questions about your application, contact us at:</p>
          <div className="contact-details">
            <div className="contact-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
                <path d="M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" />
              </svg>
              scholarship@tcu-ceaa.edu
            </div>
            <div className="contact-item">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path fillRule="evenodd" d="M1.5 4.5a3 3 0 013-3h1.372c.86 0 1.653.349 2.233.91l1.447 1.447a1.5 1.5 0 010 2.122L8.364 7.167l-.015.015m7.5 0L15.864 7.15l-.015-.015m0 0a3 3 0 013-3h1.372c.86 0 1.653.349 2.233.91l1.447 1.447a1.5 1.5 0 010 2.122L22.5 10.5v2.25a.75.75 0 01-.75.75H21a.75.75 0 01-.75-.75v-.75h-.75a.75.75 0 01-.75-.75V10.5a.75.75 0 01.75-.75h.75v-.75c0-.69-.56-1.25-1.25-1.25h-7.5c-.69 0-1.25.56-1.25 1.25v.75h.75c.414 0 .75.336.75.75v1.5a.75.75 0 01-.75.75h-.75v.75c0 .414-.336.75-.75.75H3a.75.75 0 01-.75-.75v-2.25L1.5 10.5z" clipRule="evenodd" />
              </svg>
              (032) 123-4567
            </div>
          </div>
        </div>

        <div className="timer-display">
          <p>Application submitted {formatTime(timeElapsed)} ago</p>
        </div>

        <button className="complete-btn" onClick={onComplete}>
          Return to Dashboard
        </button>
      </div>
    </div>
  );
};

export default WaitingConfirmationStep;