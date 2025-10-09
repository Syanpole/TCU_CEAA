import React, { useEffect, useState } from 'react';
import './HelpCenter.css';

interface HelpCenterProps {
  onBackToHome: () => void;
}

interface HelpTopic {
  title: string;
  description: string;
  icon: string;
  articles: Article[];
}

interface Article {
  title: string;
  content: string;
}

const HelpCenter: React.FC<HelpCenterProps> = ({ onBackToHome }) => {
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<number | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<number | null>(null);

  const helpTopics: HelpTopic[] = [
    {
      title: 'Getting Started',
      icon: '🚀',
      description: 'Learn the basics of using the TCU-CEAA Portal',
      articles: [
        {
          title: 'How to Create an Account',
          content: 'To create an account:\n1. Click "Register" on the homepage\n2. Fill in your personal information including name, student ID, and TCU email\n3. Create a strong password (minimum 8 characters)\n4. Check your email for verification link\n5. Click the link to activate your account\n6. Log in with your credentials\n\nNote: Use your official TCU email address (@tcu.edu.ph) for registration.'
        },
        {
          title: 'First Time Login',
          content: 'After creating your account:\n1. Go to the login page\n2. Enter your email and password\n3. Complete your profile information\n4. Upload required documents\n5. Review and accept terms and conditions\n\nTip: Keep your login credentials secure and never share them with anyone.'
        },
        {
          title: 'Portal Navigation Guide',
          content: 'The portal has several main sections:\n\nDashboard: View your application status and notifications\nMy Profile: Update personal information and documents\nApplications: Submit new applications and track existing ones\nDocuments: Manage uploaded files\nNotifications: View important updates\nHelp: Access support resources\n\nUse the navigation menu to access these sections quickly.'
        }
      ]
    },
    {
      title: 'Application Process',
      icon: '📝',
      description: 'Step-by-step guide to applying for CEAA',
      articles: [
        {
          title: 'How to Submit an Application',
          content: 'Follow these steps to submit your CEAA application:\n\n1. Log in to your account\n2. Navigate to "New Application"\n3. Fill out the application form completely\n4. Upload all required documents (see document requirements)\n5. Review all information for accuracy\n6. Click "Submit Application"\n7. Wait for confirmation email\n\nImportant: Once submitted, applications cannot be edited. Double-check all information before submitting.'
        },
        {
          title: 'Required Documents Checklist',
          content: 'Required documents for CEAA application:\n\n✓ Certificate of Residency (from Barangay)\n✓ Certificate of Grades/Transcript of Records\n✓ Valid Government ID\n✓ Proof of Enrollment/Registration Form\n✓ Income Tax Return OR Certificate of Indigency\n✓ Birth Certificate (PSA Copy)\n✓ 2x2 ID Photo (recent)\n\nDocument Requirements:\n- File format: PDF, JPG, or PNG\n- Maximum file size: 5MB per document\n- Documents must be clear and readable\n- Ensure all text is visible'
        },
        {
          title: 'Understanding Application Status',
          content: 'Application Status Meanings:\n\nPending: Your application has been received and is queued for review.\n\nUnder Review: CEAA committee is currently evaluating your application.\n\nIncomplete: Additional documents or information needed. Check your email for details.\n\nApproved: Congratulations! Your application has been accepted.\n\nRejected: Application was not approved. You will receive feedback via email.\n\nYou will receive email notifications when your status changes.'
        }
      ]
    },
    {
      title: 'Document Management',
      icon: '📄',
      description: 'How to upload and manage your documents',
      articles: [
        {
          title: 'How to Upload Documents',
          content: 'To upload documents:\n\n1. Go to "My Documents" or the application form\n2. Click "Upload Document" button\n3. Select the document type from dropdown\n4. Click "Choose File" and select your document\n5. Wait for upload to complete\n6. Verify document appears in your list\n\nTips:\n- Upload documents in PDF format for best results\n- Ensure documents are clear and complete\n- Check file size (max 5MB)\n- Use descriptive names for your files'
        },
        {
          title: 'Document Format Guidelines',
          content: 'Acceptable Formats:\n✓ PDF (Recommended)\n✓ JPG/JPEG\n✓ PNG\n\nFile Size Limits:\n- Maximum 5MB per file\n- Recommended: 1-2MB for faster uploads\n\nQuality Requirements:\n- Resolution: Minimum 300 DPI\n- All text must be readable\n- No blurry or cut-off portions\n- Color or black & white accepted\n\nScanning Tips:\n- Scan at 300 DPI or higher\n- Ensure good lighting\n- Avoid shadows and glare\n- Keep documents flat'
        },
        {
          title: 'Replacing or Updating Documents',
          content: 'To replace a document:\n\n1. Go to "My Documents"\n2. Find the document to replace\n3. Click "Replace" or "Update" button\n4. Upload the new document\n5. Confirm replacement\n\nNote: If your application is already under review, contact the CEAA office before replacing documents.\n\nFor incomplete applications, you can freely update documents until you resubmit.'
        }
      ]
    },
    {
      title: 'Account & Security',
      icon: '🔒',
      description: 'Manage your account and keep it secure',
      articles: [
        {
          title: 'How to Reset Your Password',
          content: 'Forgot your password?\n\n1. Go to the login page\n2. Click "Forgot Password" link\n3. Enter your registered email address\n4. Check your email for reset link\n5. Click the link (valid for 24 hours)\n6. Create a new strong password\n7. Confirm your new password\n8. Log in with new credentials\n\nPassword Requirements:\n- Minimum 8 characters\n- At least one uppercase letter\n- At least one number\n- At least one special character'
        },
        {
          title: 'Updating Profile Information',
          content: 'To update your profile:\n\n1. Log in to your account\n2. Go to "My Profile"\n3. Click "Edit Profile"\n4. Update information as needed\n5. Click "Save Changes"\n\nYou can update:\n- Contact information (phone, email)\n- Mailing address\n- Emergency contact details\n- Profile photo\n\nNote: Student ID and name changes require verification. Contact the registrar office.'
        },
        {
          title: 'Account Security Best Practices',
          content: 'Keep your account secure:\n\n✓ Use a strong, unique password\n✓ Never share your login credentials\n✓ Log out when using shared computers\n✓ Enable email notifications\n✓ Review account activity regularly\n✓ Keep your email address up to date\n✓ Don\'t click suspicious links\n✓ Report unauthorized access immediately\n\nSuspicious Activity?\nContact: security@tcu.edu.ph\nPhone: (02) 8837-8900'
        }
      ]
    },
    {
      title: 'Technical Support',
      icon: '💻',
      description: 'Troubleshooting common technical issues',
      articles: [
        {
          title: 'Browser Compatibility',
          content: 'Supported Browsers:\n✓ Google Chrome (latest version)\n✓ Mozilla Firefox (latest version)\n✓ Microsoft Edge (latest version)\n✓ Safari (latest version)\n\nNot Recommended:\n✗ Internet Explorer\n✗ Outdated browser versions\n\nFor best experience:\n1. Keep your browser updated\n2. Enable JavaScript\n3. Allow cookies\n4. Clear cache if experiencing issues\n\nMobile Devices:\nThe portal is fully responsive and works on smartphones and tablets.'
        },
        {
          title: 'Common Upload Errors',
          content: 'Upload Issues & Solutions:\n\nFile Too Large:\n- Compress PDF files\n- Reduce image resolution\n- Max size: 5MB\n\nUnsupported Format:\n- Convert to PDF, JPG, or PNG\n- Avoid HEIC, BMP, or other formats\n\nUpload Failed:\n- Check internet connection\n- Try different browser\n- Clear browser cache\n- Disable browser extensions\n\nStuck at "Uploading..."\n- Wait at least 2 minutes\n- Don\'t close the browser\n- Check file size\n- Try again with smaller file'
        },
        {
          title: 'Login Problems',
          content: 'Can\'t log in? Try these solutions:\n\nIncorrect Password:\n- Use "Forgot Password" to reset\n- Check Caps Lock\n- Copy-paste carefully if saved\n\nAccount Not Found:\n- Verify email address spelling\n- Check if you registered\n- Try the email used during registration\n\nAccount Locked:\n- Wait 30 minutes\n- Too many failed attempts locks account\n- Contact support if still locked\n\nEmail Not Verified:\n- Check spam/junk folder\n- Request new verification email\n- Verify from any device'
        }
      ]
    },
    {
      title: 'Contact & Support',
      icon: '📞',
      description: 'Get in touch with our support team',
      articles: [
        {
          title: 'How to Contact Support',
          content: 'Get help from our support team:\n\nEmail Support:\nceaa@tcu.edu.ph\nResponse time: 1-2 business days\n\nPhone Support:\n(02) 8837-8900 ext. 2100\nMonday-Friday: 8:00 AM - 5:00 PM\n\nOffice Visit:\nCEAA Office, TCU Main Campus\nGen. Santos Avenue, Central Bicutan\nTaguig City\n\nOnline Support:\nUse the "Contact Us" form in the portal\nAttach screenshots for faster resolution'
        },
        {
          title: 'Office Hours & Location',
          content: 'CEAA Office Details:\n\nOffice Hours:\nMonday - Friday: 8:00 AM - 5:00 PM\nSaturday: 8:00 AM - 12:00 PM\nSunday & Holidays: Closed\n\nLocation:\nCEAA Office\nTaguig City University Main Campus\n2nd Floor, Administration Building\nGen. Santos Avenue, Central Bicutan\nTaguig City, 1630\n\nLandmark:\nNear Taguig City Hall\nOpposite Market! Market!\n\nPublic Transport:\nJeepney: Fort Bonifacio route\nBus: EDSA Carousel to Bicutan'
        },
        {
          title: 'Reporting Issues',
          content: 'How to report problems:\n\n1. Note the Error:\n- Take a screenshot\n- Note date and time\n- Write down error message\n- Note what you were doing\n\n2. Gather Information:\n- Browser and version\n- Device type\n- Steps to reproduce\n\n3. Contact Support:\n- Email: support@tcu.edu.ph\n- Include all gathered info\n- Attach screenshots\n- Provide student ID\n\n4. Follow Up:\n- Note ticket number\n- Check email for updates\n- Respond to support queries\n\nEmergency Issues:\nCall (02) 8837-8900 ext. 2100'
        }
      ]
    }
  ];

  useEffect(() => {
    window.scrollTo(0, 0);

    const handleScroll = () => {
      setShowScrollToTop(window.pageYOffset > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleTopicClick = (index: number) => {
    setSelectedTopic(selectedTopic === index ? null : index);
    setSelectedArticle(null);
  };

  const handleArticleClick = (articleIndex: number) => {
    setSelectedArticle(selectedArticle === articleIndex ? null : articleIndex);
  };

  return (
    <div className="help-container">
      <header className="help-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <img src="/images/TCU_logo.png" alt="TCU Logo" className="logo-image" />
            </div>
            <h1 onClick={onBackToHome} style={{ cursor: 'pointer' }}>
              TCU-CEAA Portal
            </h1>
          </div>
          <button className="back-btn" onClick={onBackToHome}>
            ← Back to Home
          </button>
        </div>
      </header>

      <main className="help-main">
        <section className="help-hero">
          <div className="hero-content">
            <h2>Help Center</h2>
            <p>Find detailed guides and tutorials to help you use the portal effectively</p>
          </div>
        </section>

        <section className="help-content">
          <div className="help-topics">
            {helpTopics.map((topic, topicIndex) => (
              <div key={topicIndex} className={`topic-card ${selectedTopic === topicIndex ? 'active' : ''}`}>
                <div className="topic-header" onClick={() => handleTopicClick(topicIndex)}>
                  <div className="topic-icon-title">
                    <span className="topic-icon">{topic.icon}</span>
                    <div>
                      <h3>{topic.title}</h3>
                      <p>{topic.description}</p>
                    </div>
                  </div>
                  <svg 
                    className="expand-icon" 
                    width="24" 
                    height="24" 
                    viewBox="0 0 24 24"
                  >
                    <path 
                      d="M6 9l6 6 6-6" 
                      stroke="currentColor" 
                      strokeWidth="2" 
                      fill="none"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>

                <div className="topic-articles">
                  {topic.articles.map((article, articleIndex) => (
                    <div key={articleIndex} className="article-item">
                      <button 
                        className="article-title"
                        onClick={() => handleArticleClick(articleIndex)}
                      >
                        <span>{article.title}</span>
                        <svg width="20" height="20" viewBox="0 0 24 24">
                          <path 
                            d="M9 18l6-6-6-6" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            fill="none"
                            strokeLinecap="round"
                          />
                        </svg>
                      </button>
                      {selectedTopic === topicIndex && selectedArticle === articleIndex && (
                        <div className="article-content">
                          <div className="article-text">
                            {article.content.split('\n').map((line, i) => (
                              <p key={i}>{line}</p>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="help-contact">
          <div className="contact-box">
            <h3>Still need help?</h3>
            <p>Our support team is ready to assist you</p>
            <div className="contact-methods">
              <div className="contact-method">
                <div className="method-icon">📧</div>
                <h4>Email Us</h4>
                <p>ceaa@tcu.edu.ph</p>
                <span>Response within 1-2 business days</span>
              </div>
              <div className="contact-method">
                <div className="method-icon">📞</div>
                <h4>Call Us</h4>
                <p>(02) 8837-8900 ext. 2100</p>
                <span>Mon-Fri: 8:00 AM - 5:00 PM</span>
              </div>
              <div className="contact-method">
                <div className="method-icon">🏢</div>
                <h4>Visit Us</h4>
                <p>CEAA Office, TCU Main Campus</p>
                <span>Gen. Santos Ave, Taguig City</span>
              </div>
            </div>
          </div>
        </section>

        <section className="help-resources">
          <div className="resources-content">
            <h3>Additional Resources</h3>
            <div className="resource-links">
              <a href="https://tcu.edu.ph" target="_blank" rel="noopener noreferrer" className="resource-link">
                <div className="resource-icon">🌐</div>
                <div>
                  <h4>TCU Official Website</h4>
                  <p>Visit tcu.edu.ph for university information</p>
                </div>
              </a>
              <a href="https://scholar.taguig.gov.ph/tcu" target="_blank" rel="noopener noreferrer" className="resource-link">
                <div className="resource-icon">🎓</div>
                <div>
                  <h4>Taguig Scholarship Portal</h4>
                  <p>scholar.taguig.gov.ph/tcu</p>
                </div>
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="help-footer">
        <p>&copy; {new Date().getFullYear()} Taguig City University. All rights reserved.</p>
        <div className="footer-links">
          <a href="https://tcu.edu.ph" target="_blank" rel="noopener noreferrer">tcu.edu.ph</a>
          <span>•</span>
          <a href="https://scholar.taguig.gov.ph/tcu" target="_blank" rel="noopener noreferrer">scholar.taguig.gov.ph</a>
        </div>
      </footer>

      {showScrollToTop && (
        <button className="scroll-to-top" onClick={scrollToTop} aria-label="Scroll to top">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M12 8L6 14L7.41 15.41L12 10.83L16.59 15.41L18 14L12 8Z" fill="currentColor"/>
          </svg>
        </button>
      )}
    </div>
  );
};

export default HelpCenter;
