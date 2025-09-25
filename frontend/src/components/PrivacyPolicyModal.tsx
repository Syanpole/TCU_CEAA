import React from 'react';
import './LegalModal.css';

interface PrivacyPolicyModalProps {
  onClose: () => void;
}

const PrivacyPolicyModal: React.FC<PrivacyPolicyModalProps> = ({ onClose }) => {
  return (
    <div className="legal-modal-container">
      <div className="legal-modal-header">
        <h2>Privacy Policy</h2>
        <p>How we collect, use, and protect your personal information</p>
      </div>
      
      <div className="legal-modal-content">
        <div className="legal-section">
          <h3>Information We Collect</h3>
          <p>
            The TCU-CEAA Portal collects personal information necessary for processing 
            educational assistance applications, including:
          </p>
          <ul>
            <li>Student identification information (Student ID, full name, contact details)</li>
            <li>Academic records and enrollment status</li>
            <li>Financial information relevant to assistance eligibility</li>
            <li>Supporting documents uploaded through the portal</li>
            <li>System usage data and login information</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>How We Use Your Information</h3>
          <p>Your personal information is used exclusively for:</p>
          <ul>
            <li>Processing and evaluating educational assistance applications</li>
            <li>Verifying student eligibility and academic standing</li>
            <li>Communicating application status and program updates</li>
            <li>Maintaining accurate records for program administration</li>
            <li>Generating reports required by university and city government</li>
            <li>Improving portal services and user experience</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>Information Sharing and Disclosure</h3>
          <p>
            We do not sell, trade, or rent your personal information to third parties. 
            Information may be shared only with:
          </p>
          <ul>
            <li>Authorized TCU staff for application processing</li>
            <li>Taguig City Government officials for program administration</li>
            <li>Financial institutions for assistance disbursement</li>
            <li>Legal authorities when required by law</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>Data Security</h3>
          <p>
            We implement appropriate security measures to protect your personal information:
          </p>
          <ul>
            <li>Encrypted data transmission and storage</li>
            <li>Secure user authentication and access controls</li>
            <li>Regular security audits and system updates</li>
            <li>Limited access to authorized personnel only</li>
            <li>Secure backup and disaster recovery procedures</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>Student Rights</h3>
          <p>As a student using this portal, you have the right to:</p>
          <ul>
            <li>Access and review your personal information stored in the system</li>
            <li>Request correction of inaccurate or incomplete information</li>
            <li>Request deletion of your data after program completion (subject to legal requirements)</li>
            <li>Receive notification of any data breaches affecting your information</li>
            <li>File complaints regarding privacy concerns</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>Data Retention</h3>
          <p>
            Personal information is retained for the duration of your participation in the 
            educational assistance program and for a period thereafter as required by university 
            policies and applicable laws. Academic and financial records may be retained longer 
            for historical and audit purposes.
          </p>
        </div>

        <div className="legal-section">
          <h3>Cookies and Website Analytics</h3>
          <p>
            The portal may use cookies and similar technologies to enhance user experience, 
            maintain session security, and analyze system usage. These technologies do not 
            collect personally identifiable information beyond what you voluntarily provide.
          </p>
        </div>

        <div className="legal-section">
          <h3>Updates to Privacy Policy</h3>
          <p>
            This privacy policy may be updated periodically to reflect changes in our practices 
            or legal requirements. Users will be notified of significant changes through the 
            portal or official university communications.
          </p>
        </div>

        <div className="legal-section">
          <h3>Contact Information</h3>
          <p>
            For privacy-related questions or concerns, please contact:
          </p>
          <ul>
            <li><strong>Email:</strong> privacy@tcu.edu.ph</li>
            <li><strong>Phone:</strong> (817) 257-TCU1 (8281)</li>
            <li><strong>Office:</strong> TCU Student Affairs Office</li>
            <li><strong>Address:</strong> Gen. Santos Ave. Central Bicutan, Taguig City</li>
          </ul>
        </div>

        <div className="legal-footer">
          <p><strong>Last Updated:</strong> September 2025</p>
          <p>
            By using the TCU-CEAA Portal, you acknowledge that you have read and understood 
            this Privacy Policy and consent to the collection and use of your information 
            as described herein.
          </p>
        </div>
      </div>

      <div className="legal-modal-actions">
        <button className="legal-close-button" onClick={onClose}>
          I Understand
        </button>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal;