import React, { useEffect, useState } from 'react';
import './Privacy.css';

interface PrivacyProps {
  onBackToHome: () => void;
}

const Privacy: React.FC<PrivacyProps> = ({ onBackToHome }) => {
  const [showScrollToTop, setShowScrollToTop] = useState(false);

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

  return (
    <div className="privacy-container">
      <header className="privacy-header">
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

      <main className="privacy-main">
        <section className="privacy-hero">
          <div className="hero-content">
            <h2>Privacy Policy</h2>
            <p>Your privacy and data security are our top priorities at Taguig City University</p>
            <div className="last-updated">Last Updated: October 9, 2025</div>
          </div>
        </section>

        <section className="privacy-content">
          <div className="privacy-document">
            
            {/* Section 1: Introduction */}
            <div className="privacy-section">
              <div className="section-number">1</div>
              <div className="section-content">
                <h3>Introduction</h3>
                <p>
                  Welcome to the Taguig City University City Educational Assistance Allowance (TCU-CEAA) Portal. 
                  This Privacy Policy explains how we collect, use, protect, and share your personal information in 
                  compliance with Republic Act No. 10173, also known as the Data Privacy Act of 2012.
                </p>
                <p>
                  We are committed to protecting your privacy and ensuring the security of your personal data. By using 
                  this portal, you acknowledge that you have read and understood this Privacy Policy.
                </p>
              </div>
            </div>

            {/* Section 2: Data Privacy Act Compliance */}
            <div className="privacy-section">
              <div className="section-number">2</div>
              <div className="section-content">
                <h3>Data Privacy Act Compliance</h3>
                <p>
                  This platform fully complies with Republic Act No. 10173 (Data Privacy Act of 2012) and its 
                  Implementing Rules and Regulations. We adhere to the principles of transparency, legitimate purpose, 
                  and proportionality in all our data processing activities.
                </p>
                <h4>Our Commitments:</h4>
                <ul>
                  <li>Secure data encryption and storage using industry-standard protocols</li>
                  <li>Limited access to authorized personnel only with strict authentication</li>
                  <li>Regular security audits and vulnerability assessments</li>
                  <li>Full compliance with National Privacy Commission (NPC) guidelines</li>
                  <li>Transparent data processing practices and clear consent mechanisms</li>
                  <li>Prompt breach notification and incident response procedures</li>
                </ul>
              </div>
            </div>

            {/* Section 3: Information We Collect */}
            <div className="privacy-section">
              <div className="section-number">3</div>
              <div className="section-content">
                <h3>Information We Collect</h3>
                <p>
                  We collect only necessary information required for the CEAA application process and academic services. 
                  All data collection is done with your explicit consent and for legitimate educational purposes.
                </p>
                
                <h4>Personal Information:</h4>
                <ul>
                  <li>Full name, date of birth, and contact details</li>
                  <li>Student ID number and TCU email address</li>
                  <li>Residential address and proof of Taguig City residency</li>
                  <li>Government-issued identification documents</li>
                  <li>Emergency contact information</li>
                </ul>

                <h4>Academic Information:</h4>
                <ul>
                  <li>Current enrollment status and program details</li>
                  <li>Academic records, grades, and transcripts</li>
                  <li>Previous educational background</li>
                  <li>Scholarship history and financial assistance records</li>
                </ul>

                <h4>Financial Information:</h4>
                <ul>
                  <li>Family income details and financial need assessment</li>
                  <li>Income tax returns or certificates of indigency</li>
                  <li>Bank account information for scholarship disbursement</li>
                </ul>

                <h4>Technical Information:</h4>
                <ul>
                  <li>IP address, browser type, and device information</li>
                  <li>Login timestamps and activity logs for security</li>
                  <li>Cookies and similar tracking technologies</li>
                </ul>
              </div>
            </div>

            {/* Section 4: How We Use Your Information */}
            <div className="privacy-section">
              <div className="section-number">4</div>
              <div className="section-content">
                <h3>How We Use Your Information</h3>
                <p>Your personal information is used solely for legitimate educational and administrative purposes:</p>
                <ul>
                  <li>Processing CEAA applications and determining eligibility</li>
                  <li>Verifying identity and residency requirements</li>
                  <li>Communicating application status and important updates</li>
                  <li>Disbursing scholarship grants and financial assistance</li>
                  <li>Maintaining academic records and compliance reporting</li>
                  <li>Improving portal functionality and user experience</li>
                  <li>Conducting research and statistical analysis (anonymized)</li>
                  <li>Complying with legal obligations and university policies</li>
                </ul>
              </div>
            </div>

            {/* Section 5: Data Sharing and Disclosure */}
            <div className="privacy-section">
              <div className="section-number">5</div>
              <div className="section-content">
                <h3>Data Sharing and Disclosure</h3>
                <p>
                  We do not sell, trade, or rent your personal information to third parties. Your data may be shared 
                  only in the following limited circumstances:
                </p>
                
                <h4>Internal Sharing:</h4>
                <ul>
                  <li>With authorized TCU departments for academic and administrative purposes</li>
                  <li>With CEAA committee members for application evaluation</li>
                  <li>With university financial offices for scholarship disbursement</li>
                </ul>

                <h4>External Sharing (with consent or legal requirement):</h4>
                <ul>
                  <li>With Taguig City Government for program verification and funding</li>
                  <li>With government agencies as required by law or regulation</li>
                  <li>With law enforcement in response to valid legal requests</li>
                  <li>With accrediting bodies for institutional compliance</li>
                </ul>

                <p>
                  All third parties with access to your data are bound by strict confidentiality agreements and data 
                  protection obligations.
                </p>
              </div>
            </div>

            {/* Section 6: Your Privacy Rights */}
            <div className="privacy-section">
              <div className="section-number">6</div>
              <div className="section-content">
                <h3>Your Privacy Rights</h3>
                <p>
                  As a data subject under the Data Privacy Act, you have the following rights regarding your personal 
                  information:
                </p>
                
                <h4>Right to Information:</h4>
                <p>You have the right to be informed about the collection and processing of your personal data.</p>

                <h4>Right to Access:</h4>
                <p>You can request access to your personal data and obtain copies of the information we hold about you.</p>

                <h4>Right to Rectification:</h4>
                <p>You can request correction of inaccurate, incomplete, or outdated personal information.</p>

                <h4>Right to Erasure/Blocking:</h4>
                <p>You can request deletion or blocking of your personal data under certain circumstances.</p>

                <h4>Right to Data Portability:</h4>
                <p>You can request your data in a structured, commonly used format for transfer to another controller.</p>

                <h4>Right to Object:</h4>
                <p>You can object to certain types of data processing, including direct marketing.</p>

                <h4>Right to File a Complaint:</h4>
                <p>You can file complaints with our Data Protection Officer or the National Privacy Commission.</p>

                <p>
                  To exercise any of these rights, please contact our Data Protection Officer at dpo@tcu.edu.ph. 
                  We will respond to your request within fifteen (15) days.
                </p>
              </div>
            </div>

            {/* Section 7: Data Security Measures */}
            <div className="privacy-section">
              <div className="section-number">7</div>
              <div className="section-content">
                <h3>Data Security Measures</h3>
                <p>
                  We implement comprehensive technical, organizational, and physical security measures to protect your 
                  personal information:
                </p>

                <h4>Technical Safeguards:</h4>
                <ul>
                  <li>SSL/TLS encryption for all data transmissions</li>
                  <li>Encrypted storage of sensitive personal information</li>
                  <li>Multi-factor authentication for administrative access</li>
                  <li>Regular security patches and system updates</li>
                  <li>Intrusion detection and prevention systems</li>
                  <li>Automated backup and disaster recovery procedures</li>
                </ul>

                <h4>Organizational Safeguards:</h4>
                <ul>
                  <li>Strict access controls based on role and need-to-know</li>
                  <li>Employee training on data protection and security</li>
                  <li>Confidentiality agreements for all personnel</li>
                  <li>Regular security audits and compliance reviews</li>
                  <li>Incident response and breach notification procedures</li>
                </ul>

                <h4>Physical Safeguards:</h4>
                <ul>
                  <li>Secure server facilities with restricted access</li>
                  <li>24/7 monitoring and surveillance</li>
                  <li>Environmental controls and fire protection</li>
                </ul>

                <p>
                  While we employ industry-standard security measures, please note that no internet transmission or 
                  electronic storage is 100% secure. We cannot guarantee absolute security but continuously work to 
                  improve our protective measures.
                </p>
              </div>
            </div>

            {/* Section 8: Data Retention */}
            <div className="privacy-section">
              <div className="section-number">8</div>
              <div className="section-content">
                <h3>Data Retention Policy</h3>
                <p>
                  We retain your personal information only for as long as necessary to fulfill the purposes for which it 
                  was collected or as required by law:
                </p>
                
                <h4>Retention Periods:</h4>
                <ul>
                  <li><strong>Active Students:</strong> Throughout your enrollment and scholarship period</li>
                  <li><strong>Academic Records:</strong> Seven (7) years after graduation or program completion</li>
                  <li><strong>CEAA Application Records:</strong> Seven (7) years after final disbursement</li>
                  <li><strong>Financial Records:</strong> Ten (10) years as per COA requirements</li>
                  <li><strong>System Logs:</strong> One (1) year for security and audit purposes</li>
                </ul>

                <p>
                  After the retention period expires, personal data will be securely deleted or anonymized unless 
                  required to be retained for legal, regulatory, or legitimate business purposes.
                </p>
              </div>
            </div>

            {/* Section 9: Cookies and Tracking */}
            <div className="privacy-section">
              <div className="section-number">9</div>
              <div className="section-content">
                <h3>Cookies and Tracking Technologies</h3>
                <p>
                  The Portal uses cookies and similar technologies to enhance your experience and maintain security:
                </p>

                <h4>Types of Cookies We Use:</h4>
                <ul>
                  <li><strong>Essential Cookies:</strong> Required for portal functionality and security</li>
                  <li><strong>Session Cookies:</strong> Maintain your login state during your visit</li>
                  <li><strong>Security Cookies:</strong> Detect and prevent fraudulent activities</li>
                  <li><strong>Analytics Cookies:</strong> Help us understand usage patterns (anonymized)</li>
                </ul>

                <p>
                  You can control cookies through your browser settings, but disabling essential cookies may affect 
                  portal functionality.
                </p>
              </div>
            </div>

            {/* Section 10: Contact Information */}
            <div className="privacy-section">
              <div className="section-number">10</div>
              <div className="section-content">
                <h3>Data Protection Officer Contact</h3>
                <p>
                  For data privacy concerns, complaints, inquiries, or to exercise your privacy rights, please contact 
                  our Data Protection Officer:
                </p>

                <div className="dpo-contact-box">
                  <div className="dpo-item">
                    <strong>📧 Email</strong>
                    <p>dpo@tcu.edu.ph</p>
                  </div>
                  <div className="dpo-item">
                    <strong>📞 Phone</strong>
                    <p>(02) 8837-8900 ext. 1234</p>
                    <span>Monday-Friday: 8:00 AM - 5:00 PM</span>
                  </div>
                  <div className="dpo-item">
                    <strong>📍 Office</strong>
                    <p>Data Privacy Office</p>
                    <p>Taguig City University Main Campus</p>
                    <p>Gen. Santos Ave, Taguig City</p>
                  </div>
                </div>

                <p>
                  You may also file complaints directly with the National Privacy Commission:
                </p>
                <p>
                  <strong>National Privacy Commission</strong><br />
                  Website: <a href="https://privacy.gov.ph" target="_blank" rel="noopener noreferrer">https://privacy.gov.ph</a><br />
                  Email: info@privacy.gov.ph<br />
                  Hotline: (02) 8234-2228
                </p>
              </div>
            </div>

            {/* Consent Notice */}
            <div className="consent-notice-section">
              <div className="consent-box">
                <div className="consent-icon">
                  <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="2"/>
                    <path d="M24 16v12M24 32h.02" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <div className="consent-content">
                  <h3>Consent and Acknowledgment</h3>
                  <p>
                    By using this portal and submitting your information, you acknowledge that you have read, 
                    understood, and agree to this Privacy Policy. Your continued use of the platform constitutes 
                    your consent to the collection, processing, and storage of your personal data as described herein.
                  </p>
                  <p>
                    You may withdraw your consent at any time by contacting our Data Protection Officer, though this 
                    may affect your ability to use certain portal features or participate in the CEAA program.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </section>
      </main>

      <footer className="privacy-footer">
        <div className="footer-content">
          <p>&copy; {new Date().getFullYear()} Taguig City University. All rights reserved.</p>
          <div className="footer-links">
            <a href="https://tcu.edu.ph" target="_blank" rel="noopener noreferrer">tcu.edu.ph</a>
            <span>•</span>
            <a href="https://scholar.taguig.gov.ph/tcu" target="_blank" rel="noopener noreferrer">scholar.taguig.gov.ph</a>
          </div>
          <p className="legal-notice">
            Official portal of Taguig City University • Compliant with RA 10173 (Data Privacy Act of 2012)
          </p>
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

export default Privacy;
