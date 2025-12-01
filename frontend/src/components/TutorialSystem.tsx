import React from 'react';

interface TutorialModalProps {
  isOpen: boolean;
  onClose: () => void;
  page: string;
}

export const TutorialModal: React.FC<TutorialModalProps> = ({ isOpen, onClose, page }) => {
  if (!isOpen) return null;

  const getTutorialContent = () => {
    switch (page) {
      case 'overview':
        return {
          title: '📚 Dashboard Overview Guide',
          sections: [
            {
              icon: '🎯',
              title: 'Getting Started',
              content: 'Welcome to your scholarship dashboard! This is your central hub for managing your scholarship application.',
              steps: [
                'Monitor your application progress at the top',
                'Check important statistics in the quick stats section',
                'Use the navigation sidebar to access different sections',
                'Complete all steps to submit your application'
              ]
            },
            {
              icon: '📊',
              title: 'Progress Tracker',
              content: 'The progress bar shows how far along you are in the application process.',
              steps: [
                '<strong>Step 1:</strong> Submit all required documents',
                '<strong>Step 2:</strong> Submit your academic grades',
                '<strong>Step 3:</strong> Complete and submit your application form',
                'Each completed step will turn green with a checkmark'
              ]
            },
            {
              icon: '🔔',
              title: 'Quick Tips',
              content: '',
              steps: [
                'Click on any action card to jump to that section',
                'Use the theme toggle button to switch between light and dark mode',
                'Check the real-time updates indicator for system status',
                'Your progress is automatically saved'
              ]
            }
          ]
        };
      
      case 'documents':
        return {
          title: '📄 Documents Submission Guide',
          sections: [
            {
              icon: '📝',
              title: 'Required Documents',
              content: 'You need to submit various documents to complete your application.',
              steps: [
                '<strong>Birth Certificate:</strong> Clear copy of your NSO/PSA birth certificate',
                '<strong>School ID:</strong> Current valid school identification card',
                '<strong>Certificate of Enrollment:</strong> Official COE for current semester',
                '<strong>Voter\'s Certificate:</strong> Certificate from your local COMELEC office',
                'All documents must be clear, readable, and valid'
              ]
            },
            {
              icon: '📤',
              title: 'How to Upload',
              content: 'Follow these steps to upload your documents:',
              steps: [
                'Click the "Upload Document" button',
                'Select the document type from the dropdown',
                'Choose your file (JPG, PNG, or PDF format)',
                'Click "Submit" to upload',
                'Wait for verification from the admin'
              ]
            },
            {
              icon: '✅',
              title: 'Document Status',
              content: 'Track your document submission status:',
              steps: [
                '<strong>Pending:</strong> Document is waiting for admin review',
                '<strong>Approved:</strong> Document has been verified and accepted',
                '<strong>Rejected:</strong> Document needs to be resubmitted with corrections',
                'Check the status column to see the current state of each document'
              ]
            }
          ]
        };
      
      case 'grades':
        return {
          title: '📊 Grade Submission Guide',
          sections: [
            {
              icon: '🎓',
              title: 'Academic Requirements',
              content: 'Your grades determine your eligibility for the scholarship.',
              steps: [
                'Basic Allowance: Requires GWA of 2.5 or better',
                'Merit Incentive: Requires GWA of 1.75 or better',
                'Submit grades for each semester',
                'Include all subjects with their respective units and grades'
              ]
            },
            {
              icon: '📝',
              title: 'How to Submit Grades',
              content: 'Follow these steps to submit your grades:',
              steps: [
                'Click "Submit Grades" button',
                'Fill in Academic Year and Semester',
                'Add each subject with code, name, units, and grade',
                'The system will calculate your GWA automatically',
                'Submit for admin verification'
              ]
            },
            {
              icon: '🔍',
              title: 'Understanding Your GWA',
              content: 'Your grades are evaluated using two metrics:',
              steps: [
                '<strong>General Weighted Average (GWA):</strong> Overall average across all subjects',
                '<strong>Semestral Weighted Average:</strong> Average for the specific semester',
                'Lower numbers are better (1.0 is the highest)',
                'The system color-codes grades: green for excellent, yellow for good'
              ]
            }
          ]
        };
      
      case 'application-details':
        return {
          title: '📋 Application Process Guide',
          sections: [
            {
              icon: '📝',
              title: 'Application Steps',
              content: 'Complete your scholarship application in three stages:',
              steps: [
                '<strong>Step 1: Basic Qualification:</strong> Answer initial eligibility questions',
                '<strong>Step 2: Full Application:</strong> Complete detailed application form',
                '<strong>Step 3: Final Review:</strong> Wait for admin approval',
                'Complete documents and grades submission before applying'
              ]
            },
            {
              icon: '✍️',
              title: 'Basic Qualification',
              content: 'The first step to determine your eligibility:',
              steps: [
                'Select whether you\'re a new or renewing applicant',
                'Provide basic information about your family',
                'Answer questions about financial need',
                'Complete all fields accurately',
                'Click "Submit Qualification" when done'
              ]
            },
            {
              icon: '📄',
              title: 'Full Application Form',
              content: 'After qualifying, complete the full application:',
              steps: [
                'Fill in personal information',
                'Provide family background details',
                'Include educational information',
                'Answer financial assessment questions',
                'Review all information before submitting',
                'Once submitted, the form becomes locked'
              ]
            },
            {
              icon: '⏰',
              title: 'Important Notes',
              content: '',
              steps: [
                'Save your progress regularly while filling forms',
                'Ensure all information is accurate and truthful',
                'Submitted applications cannot be edited',
                'Check your email for updates on application status',
                'Contact support if you need to make changes after submission'
              ]
            }
          ]
        };
      
      case 'profile':
        return {
          title: '👤 Profile Settings Guide',
          sections: [
            {
              icon: '🖼️',
              title: 'Profile Picture',
              content: 'Personalize your account with a profile photo:',
              steps: [
                'Click "Upload New Photo" button',
                'Select a clear, professional photo',
                'Crop the image to fit the circle frame',
                'Click "Save" to update your profile picture',
                'Your photo appears throughout the dashboard'
              ]
            },
            {
              icon: '📧',
              title: 'Account Information',
              content: 'View and manage your account details:',
              steps: [
                'Student ID: Your unique identifier in the system',
                'Email: Used for notifications and login',
                'Name: As registered in the system',
                'Contact admin to update personal information'
              ]
            },
            {
              icon: '🔐',
              title: 'Security',
              content: 'Keep your account secure:',
              steps: [
                'Use a strong, unique password',
                'Never share your login credentials',
                'Log out when using shared computers',
                'Report any suspicious activity immediately',
                'Change your password regularly'
              ]
            }
          ]
        };
      
      default:
        return {
          title: '📚 Help & Guidance',
          sections: [
            {
              icon: '❓',
              title: 'Need Help?',
              content: 'Here are ways to get assistance:',
              steps: [
                'Click the help button (?) on any page for specific guidance',
                'Check tooltips by hovering over information icons',
                'Read the information notes on each section',
                'Contact support for technical issues',
                'Visit the help center for detailed documentation'
              ]
            }
          ]
        };
    }
  };

  const content = getTutorialContent();

  return (
    <div className="tutorial-modal-overlay" onClick={onClose}>
      <div className="tutorial-modal" onClick={(e) => e.stopPropagation()}>
        <div className="tutorial-modal-header">
          <h2>{content.title}</h2>
          <button className="tutorial-close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="tutorial-content">
          {content.sections.map((section, index) => (
            <div key={index} className="tutorial-section">
              <h3>
                <span className="tutorial-section-icon">{section.icon}</span>
                {section.title}
              </h3>
              {section.content && <p>{section.content}</p>}
              <ul>
                {section.steps.map((step, stepIndex) => (
                  <li key={stepIndex} dangerouslySetInnerHTML={{ __html: step }} />
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export const HelpTooltip: React.FC<{ text: string }> = ({ text }) => {
  return (
    <span className="help-tooltip">
      <span className="help-icon">?</span>
      <span className="tooltip-content">{text}</span>
    </span>
  );
};

export const InfoNote: React.FC<{ title: string; text: string }> = ({ title, text }) => {
  return (
    <div className="info-note">
      <div className="info-note-icon">ℹ️</div>
      <div className="info-note-content">
        <div className="info-note-title">{title}</div>
        <div className="info-note-text">{text}</div>
      </div>
    </div>
  );
};

export const PageGuideBanner: React.FC<{ icon: string; title: string; text: string }> = ({ icon, title, text }) => {
  return (
    <div className="page-guide-banner">
      <div className="guide-banner-icon">{icon}</div>
      <div className="guide-banner-content">
        <h4 className="guide-banner-title">{title}</h4>
        <p className="guide-banner-text">{text}</p>
      </div>
    </div>
  );
};

export default TutorialModal;
