import React, { useState } from 'react';
import './BiometricConsentDisclaimer.css';

interface BiometricConsentDisclaimerProps {
  onAccept: () => void;
  onDecline: () => void;
}

const BiometricConsentDisclaimer: React.FC<BiometricConsentDisclaimerProps> = ({
  onAccept,
  onDecline
}) => {
  const [accepted, setAccepted] = useState(false);
  const [readAll, setReadAll] = useState(false);

  const handleAccept = () => {
    if (accepted) {
      onAccept();
    }
  };

  return (
    <div className="biometric-consent-overlay">
      <div className="biometric-consent-modal">
        <div className="consent-modal-header">
          <h2>🔒 Biometric Data Usage Consent</h2>
          <p>Please review and accept the terms before proceeding with identity verification</p>
        </div>

        <div className="consent-modal-content">
          {/* Section 1: Automated Service */}
          <section className="consent-section">
            <div className="section-header">
              <h3>1️⃣ Automated Verification Service</h3>
              <span className="section-icon">🤖</span>
            </div>
            <div className="section-body">
              <p>
                Your identity will be verified using automated artificial intelligence services, including:
              </p>
              <ul>
                <li><strong>Liveness Detection:</strong> Advanced liveness verification to confirm you are a real person and prevent spoofing attempts.</li>
                <li><strong>Face Matching:</strong> Your live face will be automatically compared against your submitted School ID using biometric verification technology.</li>
                <li><strong>Confidence Scoring:</strong> The system will provide automated confidence scores (very high: ≥99%, high: ≥95%, medium: ≥90%, low: ≥85%, very low: &lt;85%).</li>
              </ul>
              <div className="info-box">
                <strong>⚡ Processing Time:</strong> Verification typically completes within 10-30 seconds.
              </div>
            </div>
          </section>

          {/* Section 2: Data Usage & Comparison */}
          <section className="consent-section">
            <div className="section-header">
              <h3>2️⃣ Reference Data Comparison</h3>
              <span className="section-icon">🆔</span>
            </div>
            <div className="section-body">
              <p>
                To verify your identity, the system will:
              </p>
              <ul>
                <li><strong>Capture your live face:</strong> A real-time video and still image of your face during the verification process.</li>
                <li><strong>Access your School ID image:</strong> The official ID document you previously submitted to TCU CEAA.</li>
                <li><strong>Extract facial features:</strong> Both images will be processed to extract and compare facial features using advanced facial recognition technology.</li>
                <li><strong>Calculate similarity score:</strong> The automated service will determine if your live face matches your ID at a confidence level of 99% or higher.</li>
              </ul>
              <div className="info-box">
                <strong>📋 Data Retention:</strong> Facial embeddings and liveness detection data are securely stored and used exclusively for identity verification. Raw images are processed securely with no storage on external third-party systems.
              </div>
            </div>
          </section>

          {/* Section 3: Administrative Review Override */}
          <section className="consent-section">
            <div className="section-header">
              <h3>3️⃣ Mandatory Administrative Review</h3>
              <span className="section-icon">👨‍⚖️</span>
            </div>
            <div className="section-body">
              <p>
                <strong>Important:</strong> Regardless of the automated verification result (pass or fail), your verification attempt will be reviewed by an authorized TCU CEAA administrator.
              </p>
              <ul>
                <li><strong>Human Review Required:</strong> An admin staff member will manually review your live captured image and your School ID side-by-side.</li>
                <li><strong>Final Decision Authority:</strong> The administrator has the authority to approve, reject, or request additional verification based on their professional judgment.</li>
                <li><strong>Override Capability:</strong> The admin can override any automated decision if they identify discrepancies or have concerns about the verification.</li>
                <li><strong>Security Review:</strong> The admin may also flag suspicious activity or potential fraud for further investigation.</li>
                <li><strong>Audit Trail:</strong> All administrative decisions, notes, and actions are logged for transparency and accountability.</li>
              </ul>
              <div className="info-box alert">
                <strong>🔐 Privacy & Security:</strong> Your facial data is encrypted during transmission and at rest. All verification data is handled in compliance with RA 10173 (Data Privacy Act of 2012) and institutional security policies. Your information will never be shared with third parties without explicit consent.
              </div>
            </div>
          </section>

          {/* Important Notice */}
          <div className="important-notice">
            <h4>⚠️ Important Notice</h4>
            <ul>
              <li>You must consent to biometric data collection before proceeding with identity verification.</li>
              <li>Declining consent will prevent you from submitting your allowance application at this time.</li>
              <li>You can withdraw consent and request data deletion by contacting TCU CEAA administration.</li>
              <li>This verification is required as part of the allowance application process for security and fraud prevention purposes.</li>
            </ul>
          </div>
        </div>

        {/* Acceptance Controls */}
        <div className="consent-modal-footer">
          <div className="consent-checkbox">
            <input
              type="checkbox"
              id="acceptConsent"
              checked={accepted}
              onChange={(e) => setAccepted(e.target.checked)}
              aria-label="I accept the biometric data usage terms"
            />
            <label htmlFor="acceptConsent">
              I have read and understand the above information, and I consent to the collection and use of my biometric data for identity verification purposes.
            </label>
          </div>

          <div className="consent-actions">
            <button
              type="button"
              onClick={onDecline}
              className="decline-button"
              aria-label="Decline consent and cancel verification"
            >
              Decline & Cancel
            </button>
            <button
              type="button"
              onClick={handleAccept}
              className="accept-button"
              disabled={!accepted}
              aria-label="Accept consent and proceed with verification"
            >
              Accept & Continue
            </button>
          </div>
        </div>

        {/* Version & Timestamp Info */}
        <div className="consent-footer-info">
          <small>
            Consent Version 1.0 • Effective: November 2025 • 
            <a href="#privacy-policy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
          </small>
        </div>
      </div>
    </div>
  );
};

export default BiometricConsentDisclaimer;
