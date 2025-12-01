import React from 'react';
import './GradeSubmissionDisclaimerModal.css';

interface GradeSubmissionDisclaimerModalProps {
  open: boolean;
  onClose: () => void;
  onAccept: () => void;
}

const GradeSubmissionDisclaimerModal: React.FC<GradeSubmissionDisclaimerModalProps> = ({
  open,
  onClose,
  onAccept,
}) => {
  if (!open) return null;

  return (
    <div className="disclaimer-modal-overlay" onClick={onClose}>
      <div className="disclaimer-modal" onClick={(e) => e.stopPropagation()}>
        <div className="disclaimer-header">
          <div className="disclaimer-icon">⏰</div>
          <div>
            <h2>Grade Submission Time Limit</h2>
            <p className="disclaimer-subtitle">Important information before you begin</p>
          </div>
        </div>

        <div className="disclaimer-content">
          <div className="alert alert-warning">
            <strong>⚠️ You have 2 hours to complete all grade submissions</strong>
            <p>The timer starts when you submit your first subject grade.</p>
          </div>

          <h3>Please note the following:</h3>

          <div className="disclaimer-list">
            <div className="disclaimer-item">
              <div className="item-icon time-icon">⏰</div>
              <div className="item-content">
                <h4>2-Hour Window</h4>
                <p>Once you submit your first subject grade, you must complete all remaining subjects within 2 hours.</p>
              </div>
            </div>

            <div className="disclaimer-item">
              <div className="item-icon success-icon">✅</div>
              <div className="item-content">
                <h4>Auto-Save Feature</h4>
                <p>Your progress is automatically saved as drafts. You can safely refresh your browser or close the tab and continue later (within the 2-hour window).</p>
              </div>
            </div>

            <div className="disclaimer-item">
              <div className="item-icon warning-icon">⚠️</div>
              <div className="item-content">
                <h4>Session Expiration</h4>
                <p>If the 2-hour window expires, you will need to contact the administrator to reset your submission session.</p>
              </div>
            </div>

            <div className="disclaimer-item">
              <div className="item-icon info-icon">ℹ️</div>
              <div className="item-content">
                <h4>Countdown Timer</h4>
                <p>A countdown timer will be displayed at the top of the form showing your remaining time.</p>
              </div>
            </div>
          </div>

          <div className="alert alert-info">
            <strong>💡 Tip:</strong> Prepare all your grade sheets before starting the submission process to ensure you have enough time to complete everything.
          </div>
        </div>

        <div className="disclaimer-actions">
          <button className="btn-cancel" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-accept" onClick={onAccept}>
            I Understand, Start Submission
          </button>
        </div>
      </div>
    </div>
  );
};

export default GradeSubmissionDisclaimerModal;
