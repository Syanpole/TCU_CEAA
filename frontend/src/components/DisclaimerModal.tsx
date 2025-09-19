import React from 'react';
import './LegalModal.css';

interface DisclaimerModalProps {
  onClose: () => void;
}

const DisclaimerModal: React.FC<DisclaimerModalProps> = ({ onClose }) => {
  return (
    <div className="legal-modal-container">
      <div className="legal-modal-header">
        <h2>Disclaimer</h2>
        <p>Important information regarding the TCU-CEAA Portal</p>
      </div>
      
      <div className="legal-modal-content">
        <div className="legal-section">
          <h3>Educational Assistance Program</h3>
          <p>
            The Taguig City University - City Educational Assistance Allowance (TCU-CEAA) Portal 
            is an official platform designed to facilitate the application and management of 
            educational financial assistance for qualified TCU students.
          </p>
        </div>

        <div className="legal-section">
          <h3>Eligibility and Requirements</h3>
          <ul>
            <li>Financial assistance is subject to availability of funds and budget allocation</li>
            <li>All applications must meet the eligibility criteria set by Taguig City Government</li>
            <li>Students must maintain academic standing requirements to continue receiving assistance</li>
            <li>Assistance amounts and schedules may vary based on program policies</li>
          </ul>
        </div>

        <div className="legal-section">
          <h3>Application Process</h3>
          <p>
            While we strive to process applications efficiently, approval and disbursement of 
            educational assistance is not guaranteed and depends on various factors including 
            but not limited to available budget, eligibility verification, and compliance with 
            program requirements.
          </p>
        </div>

        <div className="legal-section">
          <h3>Information Accuracy</h3>
          <p>
            Students are responsible for providing accurate and truthful information in their 
            applications. Any false or misleading information may result in disqualification 
            from the program and potential legal consequences.
          </p>
        </div>

        <div className="legal-section">
          <h3>System Availability</h3>
          <p>
            The TCU-CEAA Portal is provided "as is" and may experience periodic maintenance, 
            updates, or temporary unavailability. We are not responsible for any inconvenience 
            caused by system downtime or technical issues.
          </p>
        </div>

        <div className="legal-section">
          <h3>Changes to Terms</h3>
          <p>
            Taguig City University and the City Government of Taguig reserve the right to 
            modify program terms, eligibility requirements, and assistance amounts at any time 
            without prior notice, subject to applicable laws and regulations.
          </p>
        </div>

        <div className="legal-section">
          <h3>Contact Information</h3>
          <p>
            For questions about the educational assistance program, please contact the 
            TCU Student Affairs Office or visit the university campus during office hours.
          </p>
        </div>

        <div className="legal-footer">
          <p><strong>Last Updated:</strong> September 2025</p>
          <p>
            This disclaimer is subject to change. Students are advised to review this 
            information regularly for any updates.
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

export default DisclaimerModal;