import React from 'react';
import './VerificationLimitModal.css';

interface VerificationLimitModalProps {
  isOpen: boolean;
  onClose: () => void;
  dailyCount: number;
  maxAttempts: number;
  retryAfter?: number;
}

const VerificationLimitModal: React.FC<VerificationLimitModalProps> = ({
  isOpen,
  onClose,
  dailyCount,
  maxAttempts,
  retryAfter = 86400
}) => {
  if (!isOpen) return null;

  const hoursRemaining = Math.ceil(retryAfter / 3600);
  const nextRetryTime = new Date(Date.now() + retryAfter * 1000);
  const formattedTime = nextRetryTime.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="verification-limit-modal-overlay" onClick={onClose}>
      <div className="verification-limit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="icon-container">
            <svg className="limit-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 7V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="12" cy="16" r="1" fill="currentColor"/>
            </svg>
          </div>
          <h2>Daily Verification Limit Reached</h2>
        </div>

        <div className="modal-body">
          <div className="limit-info">
            <div className="info-card">
              <div className="info-label">Attempts Today</div>
              <div className="info-value">{dailyCount} / {maxAttempts}</div>
            </div>
            <div className="info-card">
              <div className="info-label">Reset In</div>
              <div className="info-value">{hoursRemaining}h</div>
            </div>
          </div>

          <div className="message-container">
            <p className="main-message">
              You've reached the maximum number of face verification attempts for today.
            </p>
            <p className="sub-message">
              For security reasons, we limit verification attempts to prevent fraud and protect your account.
            </p>
          </div>

          <div className="reset-info">
            <svg className="clock-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <div>
              <div className="reset-label">Your limit will reset on:</div>
              <div className="reset-time">{formattedTime}</div>
            </div>
          </div>

          <div className="support-section">
            <h3>Need Help?</h3>
            <p>If you're experiencing issues with face verification or need immediate assistance:</p>
            <ul>
              <li>Contact our support team at <strong>support@tcu.edu</strong></li>
              <li>Call us at <strong>(02) 8888-1234</strong></li>
              <li>Visit the TCU scholarship office during business hours</li>
            </ul>
          </div>

          <div className="tips-section">
            <h3>Tips for Successful Verification</h3>
            <ul>
              <li>🌞 Ensure you're in a well-lit area</li>
              <li>😊 Remove glasses and face coverings</li>
              <li>📱 Hold your device at eye level</li>
              <li>👤 Follow the on-screen instructions carefully</li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button className="close-button" onClick={onClose}>
            I Understand
          </button>
        </div>
      </div>
    </div>
  );
};

export default VerificationLimitModal;
