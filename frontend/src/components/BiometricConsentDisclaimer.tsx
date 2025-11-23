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
                Your identity will be verified using automated artificial intelligence services powered by AWS Rekognition, including:
              </p>
              <ul>
                <li><strong>Liveness Check:</strong> You will be asked to perform a brief video selfie (3D liveness challenge) to confirm you are a real person and not a photo, video replay, or deepfake.</li>
                <li><strong>Identity Comparison:</strong> Your live face will be compared against the School ID photo you submitted, using advanced facial recognition technology with a strict &gt;99% similarity threshold.</li>
                <li><strong>Confidence Scoring:</strong> The system provides automated confidence levels (very high: ≥99%, high: ≥95%, medium: ≥90%, low: ≥85%, very low: &lt;85%).</li>
              </ul>
              <div className="info-box">
                <strong>⚡ Processing Time:</strong> Verification typically completes within 30-60 seconds due to cross-cloud processing.
              </div>
            </div>
          </section>

          {/* Section 2: Data Usage & Comparison */}
          <section className="consent-section">
            <div className="section-header">
              <h3>2️⃣ Data Processing</h3>
              <span className="section-icon">🆔</span>
            </div>
            <div className="section-body">
              <p>
                Your biometric data is processed securely via Google Cloud (where this application is hosted) and Amazon Web Services (AWS) Rekognition for facial analysis:
              </p>
              <ul>
                <li><strong>Video Capture:</strong> A brief video selfie is recorded during the 3D liveness challenge to detect real human presence.</li>
                <li><strong>Reference Image Extraction:</strong> AWS Rekognition extracts a high-quality reference image from your liveness video for comparison.</li>
                <li><strong>School ID Comparison:</strong> Your reference image is compared against the face in your submitted School ID document.</li>
                <li><strong>Audit Trail:</strong> Liveness session data (including audit images) is stored in AWS S3 with encryption for administrative review.</li>
              </ul>
              <div className="info-box">
                <strong>📋 Data Retention:</strong> Biometric data is retained for verification audit purposes only. All data transmission is encrypted, and your information is never shared with unauthorized third parties.
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
                <strong>Important:</strong> While our system uses automated biometric analysis with high accuracy, ALL verifications require mandatory human review by authorized TCU CEAA administrators before final approval.
              </p>
              <ul>
                <li><strong>Human-in-the-Loop Security:</strong> Every verification (regardless of AI confidence score) is sent to an admin review queue.</li>
                <li><strong>Side-by-Side Comparison:</strong> Administrators manually inspect your liveness reference image alongside your School ID photo.</li>
                <li><strong>Final Decision Authority:</strong> The administrator has absolute authority to approve, reject, or request re-verification based on their professional judgment.</li>
                <li><strong>Override Capability:</strong> Admins can override any automated result if they detect discrepancies, quality issues, or fraud indicators.</li>
                <li><strong>Security Escalation:</strong> Suspicious cases may be escalated for enhanced fraud investigation.</li>
              </ul>
              <div className="info-box alert">
                <strong>🔐 Privacy & Security:</strong> Your biometric data is encrypted during transmission and at rest. All processing complies with RA 10173 (Data Privacy Act of 2012). Your information will never be shared with unauthorized third parties.
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
