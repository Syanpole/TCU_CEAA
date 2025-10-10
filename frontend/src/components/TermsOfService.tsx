import React, { useEffect, useState } from 'react';
import './TermsOfService.css';

interface TermsOfServiceProps {
  onBackToHome: () => void;
}

const TermsOfService: React.FC<TermsOfServiceProps> = ({ onBackToHome }) => {
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const [accepted, setAccepted] = useState(false);

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
    <div className="terms-container">
      <header className="terms-header">
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

      <main className="terms-main">
        <section className="terms-hero">
          <div className="hero-content">
            <h2>Terms of Service</h2>
            <p>Please read these terms carefully before using the TCU-CEAA Portal</p>
            <div className="last-updated">Last Updated: October 9, 2025</div>
          </div>
        </section>

        <section className="terms-content">
          <div className="terms-document">
            
            {/* Section 1 */}
            <div className="terms-section">
              <div className="section-number">1</div>
              <div className="section-content">
                <h3>Acceptance of Terms</h3>
                <p>
                  By accessing and using the Taguig City University City Educational Assistance Allowance (TCU-CEAA) Portal 
                  (hereinafter referred to as "the Portal"), you acknowledge that you have read, understood, and agree to be 
                  bound by these Terms of Service and our Privacy Policy.
                </p>
                <p>
                  If you do not agree to these terms, you must not access or use the Portal. Your continued use of the Portal 
                  constitutes acceptance of any modifications to these terms.
                </p>
              </div>
            </div>

            {/* Section 2 */}
            <div className="terms-section">
              <div className="section-number">2</div>
              <div className="section-content">
                <h3>Eligibility & User Accounts</h3>
                <h4>2.1 Eligibility Requirements</h4>
                <p>To use this Portal, you must:</p>
                <ul>
                  <li>Be a currently enrolled student at Taguig City University</li>
                  <li>Be a bonafide resident of Taguig City with valid proof of residency</li>
                  <li>Possess a valid TCU student ID and official TCU email address (@tcu.edu.ph)</li>
                  <li>Be at least 18 years of age, or have parental/guardian consent if under 18</li>
                  <li>Meet the academic and financial requirements for CEAA eligibility</li>
                </ul>

                <h4>2.2 Account Registration</h4>
                <p>When creating an account, you agree to:</p>
                <ul>
                  <li>Provide accurate, current, and complete information</li>
                  <li>Maintain and promptly update your account information</li>
                  <li>Maintain the security and confidentiality of your password</li>
                  <li>Accept responsibility for all activities under your account</li>
                  <li>Immediately notify us of any unauthorized use of your account</li>
                </ul>

                <h4>2.3 Account Restrictions</h4>
                <p>
                  Each user is permitted only one account. Creating multiple accounts may result in immediate suspension 
                  and disqualification from the CEAA program. Taguig City University reserves the right to suspend or 
                  terminate accounts that violate these terms.
                </p>
              </div>
            </div>

            {/* Section 3 */}
            <div className="terms-section">
              <div className="section-number">3</div>
              <div className="section-content">
                <h3>Portal Use & Acceptable Conduct</h3>
                <h4>3.1 Permitted Uses</h4>
                <p>This Portal is provided exclusively for:</p>
                <ul>
                  <li>Submitting CEAA applications and required documentation</li>
                  <li>Tracking application status and receiving notifications</li>
                  <li>Communicating with CEAA administrators regarding your application</li>
                  <li>Accessing scholarship information and program updates</li>
                  <li>Managing your personal profile and academic records</li>
                </ul>

                <h4>3.2 Prohibited Activities</h4>
                <p>You agree NOT to:</p>
                <ul>
                  <li>Submit false, misleading, or fraudulent information</li>
                  <li>Impersonate another person or entity</li>
                  <li>Upload malicious software, viruses, or harmful code</li>
                  <li>Attempt to gain unauthorized access to any part of the Portal</li>
                  <li>Interfere with or disrupt the Portal's operation or servers</li>
                  <li>Scrape, harvest, or collect data from the Portal using automated means</li>
                  <li>Use the Portal for any commercial or unauthorized purpose</li>
                  <li>Share your login credentials with others</li>
                  <li>Manipulate, alter, or forge documents submitted to the Portal</li>
                </ul>

                <h4>3.3 Consequences of Violations</h4>
                <p>
                  Violation of these terms may result in: immediate account suspension, permanent termination of access, 
                  disqualification from CEAA benefits, academic disciplinary action, and/or legal action as appropriate 
                  under Philippine law.
                </p>
              </div>
            </div>

            {/* Section 4 */}
            <div className="terms-section">
              <div className="section-number">4</div>
              <div className="section-content">
                <h3>Data Privacy & Information Security</h3>
                <h4>4.1 Compliance with Data Privacy Act</h4>
                <p>
                  The Portal fully complies with Republic Act No. 10173 (Data Privacy Act of 2012). We are committed to 
                  protecting your personal information and ensuring its confidentiality, integrity, and availability.
                </p>

                <h4>4.2 Information Collection & Use</h4>
                <p>By using this Portal, you consent to:</p>
                <ul>
                  <li>Collection of personal and academic information necessary for CEAA processing</li>
                  <li>Storage of your data in secure university databases</li>
                  <li>Processing of your information by authorized CEAA personnel</li>
                  <li>Sharing of information with relevant university departments as needed</li>
                  <li>Retention of records as required by university policies and Philippine law</li>
                </ul>

                <h4>4.3 Your Data Rights</h4>
                <p>
                  You have the right to access, correct, erase, or port your personal data. For data privacy concerns, 
                  please contact our Data Protection Officer at dpo@tcu.edu.ph. For complete details, please review our 
                  Privacy Policy.
                </p>
              </div>
            </div>

            {/* Section 5 */}
            <div className="terms-section">
              <div className="section-number">5</div>
              <div className="section-content">
                <h3>Application Process & Requirements</h3>
                <h4>5.1 Application Submission</h4>
                <p>
                  All applications must be submitted through the Portal within designated application periods. Late or 
                  incomplete applications may not be considered. Once submitted, applications cannot be edited. Users are 
                  responsible for reviewing all information carefully before submission.
                </p>

                <h4>5.2 Document Requirements</h4>
                <p>All submitted documents must be:</p>
                <ul>
                  <li>Authentic, complete, and unaltered original documents or certified true copies</li>
                  <li>In acceptable file formats (PDF, JPG, PNG) and within size limits (max 5MB)</li>
                  <li>Clear, readable, and properly oriented</li>
                  <li>Submitted within the specified deadlines</li>
                </ul>

                <h4>5.3 Verification & Review</h4>
                <p>
                  Taguig City University reserves the right to verify all submitted information and documents. False or 
                  fraudulent submissions will result in immediate disqualification and may lead to academic disciplinary 
                  action or legal consequences.
                </p>

                <h4>5.4 Application Decisions</h4>
                <p>
                  CEAA application decisions are final and are made at the sole discretion of Taguig City University. 
                  The university is not obligated to provide detailed explanations for rejected applications but may provide 
                  general feedback upon request.
                </p>
              </div>
            </div>

            {/* Section 6 */}
            <div className="terms-section">
              <div className="section-number">6</div>
              <div className="section-content">
                <h3>Intellectual Property Rights</h3>
                <h4>6.1 Portal Ownership</h4>
                <p>
                  All content, features, and functionality of the Portal, including but not limited to text, graphics, logos, 
                  icons, images, software, and design, are owned by Taguig City University and are protected by Philippine 
                  and international copyright, trademark, and other intellectual property laws.
                </p>

                <h4>6.2 Limited License</h4>
                <p>
                  You are granted a limited, non-exclusive, non-transferable license to access and use the Portal for its 
                  intended educational and administrative purposes only. This license does not permit you to modify, 
                  reproduce, distribute, or create derivative works from any Portal content.
                </p>

                <h4>6.3 Trademarks</h4>
                <p>
                  "Taguig City University," "TCU," the TCU logo, and other TCU marks are trademarks of Taguig City University. 
                  You may not use these marks without prior written permission from the university.
                </p>
              </div>
            </div>

            {/* Section 7 */}
            <div className="terms-section">
              <div className="section-number">7</div>
              <div className="section-content">
                <h3>Disclaimers & Limitations of Liability</h3>
                <h4>7.1 Service Availability</h4>
                <p>
                  The Portal is provided "as is" and "as available" without warranties of any kind. We do not guarantee 
                  that the Portal will be uninterrupted, error-free, or free from viruses or other harmful components. 
                  The university may suspend or discontinue the Portal for maintenance or updates without prior notice.
                </p>

                <h4>7.2 Accuracy of Information</h4>
                <p>
                  While we strive to maintain accurate information, Taguig City University makes no warranties regarding 
                  the accuracy, completeness, or reliability of any content on the Portal. Program requirements, eligibility 
                  criteria, and policies may change without prior notice.
                </p>

                <h4>7.3 Limitation of Liability</h4>
                <p>
                  To the fullest extent permitted by law, Taguig City University, its officers, employees, and affiliates 
                  shall not be liable for any indirect, incidental, consequential, or punitive damages arising from your 
                  use or inability to use the Portal, including but not limited to: loss of data, loss of scholarship 
                  opportunities, technical difficulties, or system downtime.
                </p>

                <h4>7.4 External Links</h4>
                <p>
                  The Portal may contain links to third-party websites or resources. We are not responsible for the content, 
                  privacy practices, or security of external sites. Your use of third-party sites is at your own risk.
                </p>
              </div>
            </div>

            {/* Section 8 */}
            <div className="terms-section">
              <div className="section-number">8</div>
              <div className="section-content">
                <h3>Program-Specific Terms</h3>
                <h4>8.1 CEAA Eligibility Maintenance</h4>
                <p>Recipients of CEAA benefits must:</p>
                <ul>
                  <li>Maintain required academic standing and GPA throughout the scholarship period</li>
                  <li>Remain enrolled as a full-time student at Taguig City University</li>
                  <li>Continue to meet residency requirements in Taguig City</li>
                  <li>Comply with all university policies and codes of conduct</li>
                  <li>Promptly report any changes in eligibility status</li>
                </ul>

                <h4>8.2 Scholarship Obligations</h4>
                <p>
                  CEAA recipients may be required to: participate in university service programs, attend scholarship 
                  orientations and seminars, submit periodic progress reports, or fulfill other reasonable obligations 
                  as specified by the CEAA program.
                </p>

                <h4>8.3 Revocation of Benefits</h4>
                <p>
                  CEAA benefits may be revoked if you: fail to maintain eligibility requirements, violate university 
                  policies, provide false information, or fail to meet scholarship obligations. Revocation decisions 
                  are at the sole discretion of Taguig City University.
                </p>
              </div>
            </div>

            {/* Section 9 */}
            <div className="terms-section">
              <div className="section-number">9</div>
              <div className="section-content">
                <h3>Modifications to Terms</h3>
                <p>
                  Taguig City University reserves the right to modify, amend, or update these Terms of Service at any time 
                  without prior notice. Changes will be effective immediately upon posting to the Portal. Your continued use 
                  of the Portal after modifications constitutes acceptance of the updated terms.
                </p>
                <p>
                  We encourage you to review these Terms periodically. Material changes will be communicated through the 
                  Portal or via your registered email address.
                </p>
              </div>
            </div>

            {/* Section 10 */}
            <div className="terms-section">
              <div className="section-number">10</div>
              <div className="section-content">
                <h3>Governing Law & Dispute Resolution</h3>
                <h4>10.1 Applicable Law</h4>
                <p>
                  These Terms of Service shall be governed by and construed in accordance with the laws of the Republic of 
                  the Philippines, without regard to conflict of law provisions.
                </p>

                <h4>10.2 Jurisdiction</h4>
                <p>
                  Any disputes arising from or relating to these Terms or your use of the Portal shall be subject to the 
                  exclusive jurisdiction of the courts of Taguig City, Philippines.
                </p>

                <h4>10.3 Dispute Resolution</h4>
                <p>
                  Before pursuing formal legal action, parties agree to attempt to resolve disputes through good faith 
                  negotiations. Unresolved disputes may be escalated through appropriate university channels before 
                  resorting to litigation.
                </p>
              </div>
            </div>

            {/* Section 11 */}
            <div className="terms-section">
              <div className="section-number">11</div>
              <div className="section-content">
                <h3>Contact Information</h3>
                <p>For questions, concerns, or issues regarding these Terms of Service, please contact:</p>
                
                <div className="contact-info-box">
                  <div className="contact-item">
                    <strong>CEAA Office</strong>
                    <p>Taguig City University Main Campus</p>
                    <p>Gen. Santos Avenue, Central Bicutan</p>
                    <p>Taguig City, 1630 Philippines</p>
                  </div>
                  
                  <div className="contact-item">
                    <strong>Email</strong>
                    <p>ceaa@tcu.edu.ph</p>
                    <p>info@tcu.edu.ph</p>
                  </div>
                  
                  <div className="contact-item">
                    <strong>Phone</strong>
                    <p>(02) 8837-8900</p>
                    <p>Monday-Friday: 8:00 AM - 5:00 PM</p>
                  </div>
                  
                  <div className="contact-item">
                    <strong>Website</strong>
                    <p><a href="https://tcu.edu.ph" target="_blank" rel="noopener noreferrer">https://tcu.edu.ph</a></p>
                    <p><a href="https://scholar.taguig.gov.ph/tcu" target="_blank" rel="noopener noreferrer">https://scholar.taguig.gov.ph/tcu</a></p>
                  </div>
                </div>
              </div>
            </div>

            {/* Section 12 */}
            <div className="terms-section">
              <div className="section-number">12</div>
              <div className="section-content">
                <h3>Severability & Entire Agreement</h3>
                <h4>12.1 Severability</h4>
                <p>
                  If any provision of these Terms is found to be invalid, illegal, or unenforceable, the remaining 
                  provisions shall continue in full force and effect.
                </p>

                <h4>12.2 Entire Agreement</h4>
                <p>
                  These Terms of Service, together with our Privacy Policy and any other legal notices published on the 
                  Portal, constitute the entire agreement between you and Taguig City University regarding your use of 
                  the Portal.
                </p>

                <h4>12.3 No Waiver</h4>
                <p>
                  The failure of Taguig City University to enforce any right or provision of these Terms shall not be 
                  deemed a waiver of such right or provision.
                </p>
              </div>
            </div>

            {/* Acknowledgment */}
            <div className="terms-acknowledgment">
              <div className="acknowledgment-box">
                <h3>Acknowledgment</h3>
                <p>
                  By using the TCU-CEAA Portal, you acknowledge that you have read these Terms of Service, understand 
                  them, and agree to be bound by their provisions. If you do not agree to these terms, please discontinue 
                  use of the Portal immediately.
                </p>
                <div className="acceptance-notice">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  <p>
                    Your use of this portal constitutes acceptance of these Terms of Service and our Privacy Policy.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </section>
      </main>

      <footer className="terms-footer">
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

export default TermsOfService;
