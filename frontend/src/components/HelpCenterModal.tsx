import React, { useState } from 'react';
import './HelpModal.css';

interface HelpCenterModalProps {
  onClose: () => void;
}

interface HelpSection {
  id: number;
  title: string;
  icon: string;
  content: React.ReactNode;
}

const HelpCenterModal: React.FC<HelpCenterModalProps> = ({ onClose }) => {
  const [activeSection, setActiveSection] = useState<number>(1);

  const helpSections: HelpSection[] = [
    {
      id: 1,
      title: "Getting Started",
      icon: "🚀",
      content: (
        <div>
          <h3>Welcome to TCU-CEAA Portal</h3>
          <p>Follow these steps to get started with your educational assistance application:</p>
          
          <div className="step-guide">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Create Your Account</h4>
                <p>Click "Student Registration" on the homepage and fill out the registration form with your personal information.</p>
                <ul>
                  <li>Use your official TCU email address</li>
                  <li>Provide accurate student ID number</li>
                  <li>Create a strong password</li>
                </ul>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Verify Your Email</h4>
                <p>Check your email inbox for a verification link and click it to activate your account.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Complete Your Profile</h4>
                <p>Log in and complete your profile with all required information including contact details and academic information.</p>
              </div>
            </div>
            
            <div className="step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h4>Start Your Application</h4>
                <p>Navigate to the application section and begin your educational assistance application.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 2,
      title: "Application Guide",
      icon: "📝",
      content: (
        <div>
          <h3>How to Apply for Educational Assistance</h3>
          
          <div className="guide-section">
            <h4>📋 Required Documents Checklist</h4>
            <div className="document-checklist">
              <label><input type="checkbox" /> Valid ID with photo</label>
              <label><input type="checkbox" /> Certificate of enrollment/registration</label>
              <label><input type="checkbox" /> Latest grades/transcript</label>
              <label><input type="checkbox" /> Proof of Taguig City residency</label>
              <label><input type="checkbox" /> Birth certificate</label>
              <label><input type="checkbox" /> Income certification (if required)</label>
            </div>
          </div>
          
          <div className="guide-section">
            <h4>📤 Document Upload Tips</h4>
            <ul>
              <li><strong>File formats:</strong> PDF, JPG, PNG only</li>
              <li><strong>File size:</strong> Maximum 5MB per document</li>
              <li><strong>Quality:</strong> Ensure documents are clear and readable</li>
              <li><strong>Naming:</strong> Use descriptive filenames (e.g., "transcript_2024.pdf")</li>
            </ul>
          </div>
          
          <div className="guide-section">
            <h4>⏱️ Application Timeline</h4>
            <div className="timeline">
              <div className="timeline-item">
                <strong>Day 1:</strong> Submit complete application
              </div>
              <div className="timeline-item">
                <strong>Days 2-3:</strong> Initial review and document verification
              </div>
              <div className="timeline-item">
                <strong>Days 4-7:</strong> Eligibility assessment
              </div>
              <div className="timeline-item">
                <strong>Days 8-10:</strong> Final approval and notification
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 3,
      title: "Account Management",
      icon: "👤",
      content: (
        <div>
          <h3>Managing Your Account</h3>
          
          <div className="guide-section">
            <h4>🔑 Password Management</h4>
            <p><strong>To change your password:</strong></p>
            <ol>
              <li>Go to your profile settings</li>
              <li>Click "Change Password"</li>
              <li>Enter your current password</li>
              <li>Enter and confirm your new password</li>
              <li>Click "Update Password"</li>
            </ol>
            
            <p><strong>Password Requirements:</strong></p>
            <ul>
              <li>At least 8 characters long</li>
              <li>Include uppercase and lowercase letters</li>
              <li>Include at least one number</li>
              <li>Include at least one special character</li>
            </ul>
          </div>
          
          <div className="guide-section">
            <h4>📧 Updating Contact Information</h4>
            <p>To update your contact details:</p>
            <ol>
              <li>Navigate to "Profile Settings"</li>
              <li>Click "Edit Information"</li>
              <li>Update your email, phone, or address</li>
              <li>Save changes</li>
            </ol>
            <div className="alert-box">
              <strong>Important:</strong> Keep your contact information current to receive important notifications about your application.
            </div>
          </div>
          
          <div className="guide-section">
            <h4>🔒 Account Security</h4>
            <ul>
              <li>Never share your login credentials</li>
              <li>Log out from shared computers</li>
              <li>Report suspicious account activity immediately</li>
              <li>Use a unique password for your TCU-CEAA account</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 4,
      title: "Troubleshooting",
      icon: "🔧",
      content: (
        <div>
          <h3>Common Issues & Solutions</h3>
          
          <div className="troubleshoot-item">
            <h4>❌ Can't Log In</h4>
            <p><strong>Possible solutions:</strong></p>
            <ul>
              <li>Check if your email address is correctly entered</li>
              <li>Use the "Forgot Password" feature to reset your password</li>
              <li>Clear your browser cache and cookies</li>
              <li>Try using a different browser</li>
              <li>Ensure your internet connection is stable</li>
            </ul>
          </div>
          
          <div className="troubleshoot-item">
            <h4>📁 Document Upload Failed</h4>
            <p><strong>Check the following:</strong></p>
            <ul>
              <li>File size is under 5MB</li>
              <li>File format is PDF, JPG, or PNG</li>
              <li>Internet connection is stable</li>
              <li>Document is not corrupted</li>
              <li>Try uploading one document at a time</li>
            </ul>
          </div>
          
          <div className="troubleshoot-item">
            <h4>📧 Not Receiving Emails</h4>
            <p><strong>Steps to resolve:</strong></p>
            <ul>
              <li>Check your spam/junk folder</li>
              <li>Verify your email address in your profile</li>
              <li>Add ceaa@tcu.edu.ph to your contacts</li>
              <li>Check if your email quota is full</li>
            </ul>
          </div>
          
          <div className="troubleshoot-item">
            <h4>🐌 Slow Performance</h4>
            <p><strong>Try these solutions:</strong></p>
            <ul>
              <li>Close unnecessary browser tabs</li>
              <li>Clear browser cache</li>
              <li>Check your internet speed</li>
              <li>Try accessing during off-peak hours</li>
              <li>Use a supported browser (Chrome, Firefox, Edge)</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 5,
      title: "Contact Support",
      icon: "📞",
      content: (
        <div>
          <h3>Get Additional Help</h3>
          
          <div className="contact-grid">
            <div className="contact-card">
              <h4>📧 Email Support</h4>
              <p><strong>ceaa@tcu.edu.ph</strong></p>
              <p>For general inquiries and technical issues</p>
              <p><em>Response time: 24-48 hours</em></p>
            </div>
            
            <div className="contact-card">
              <h4>📞 Phone Support</h4>
              <p><strong>(817) 257-TCU1 (8281)</strong></p>
              <p>Monday - Friday: 8:00 AM - 5:00 PM</p>
              <p><em>For urgent assistance</em></p>
            </div>
            
            <div className="contact-card">
              <h4>🏢 Office Visit</h4>
              <p><strong>TCU Student Affairs Office</strong></p>
              <p>Gen. Santos Ave. Central Bicutan<br/>Taguig City, Philippines</p>
              <p><em>Monday - Friday: 8:00 AM - 5:00 PM</em></p>
            </div>
            
            <div className="contact-card">
              <h4>💬 Live Chat</h4>
              <p><strong>Available on portal</strong></p>
              <p>Monday - Friday: 9:00 AM - 4:00 PM</p>
              <p><em>Quick assistance for simple questions</em></p>
            </div>
          </div>
          
          <div className="guide-section">
            <h4>📝 When Contacting Support</h4>
            <p>Please include the following information:</p>
            <ul>
              <li>Your full name and student ID</li>
              <li>Your registered email address</li>
              <li>Detailed description of the issue</li>
              <li>Steps you've already tried</li>
              <li>Screenshots (if applicable)</li>
              <li>Browser and device information</li>
            </ul>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="help-modal-container">
      <div className="help-modal-header">
        <h2>Help Center</h2>
        <p>Comprehensive guides and support for using the TCU-CEAA Portal</p>
      </div>
      
      <div className="help-modal-body">
        <div className="help-sidebar">
          {helpSections.map(section => (
            <button
              key={section.id}
              className={`help-nav-item ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              <span className="help-icon">{section.icon}</span>
              <span className="help-title">{section.title}</span>
            </button>
          ))}
        </div>
        
        <div className="help-content">
          {helpSections.find(section => section.id === activeSection)?.content}
        </div>
      </div>

      <div className="help-modal-actions">
        <div className="help-footer-info">
          <p>Need more help? Contact our support team at <strong>ceaa@tcu.edu.ph</strong></p>
        </div>
        <button className="help-close-button" onClick={onClose}>
          Close Help Center
        </button>
      </div>
    </div>
  );
};

export default HelpCenterModal;