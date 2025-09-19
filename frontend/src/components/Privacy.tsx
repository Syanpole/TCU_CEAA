import React, { useEffect, useState } from 'react';
import './Privacy.css';

interface PrivacyProps {
  onBackToHome: () => void;
}

const Privacy: React.FC<PrivacyProps> = ({ onBackToHome }) => {
  const [showScrollToTop, setShowScrollToTop] = useState(false);

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
    
    // Scroll animation observer
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate');
          // Stop observing this element once it's animated
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    // Observe all sections
    const sections = document.querySelectorAll('.animate-section');
    sections.forEach(section => observer.observe(section));

    // Scroll to top button visibility
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      setShowScrollToTop(scrollTop > 300);
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  return (
    <div className="privacy-container">
      <header className="privacy-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <img src="/images/TCU_logo.png" alt="TCU Logo" className="logo-image" />
            </div>
            <h1 
              className="clickable-title" 
              onClick={onBackToHome}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              TCU-CEAA Portal
            </h1>
          </div>
          <div className="privacy-nav">
            <button className="back-btn" onClick={onBackToHome}>
              ← Back to Home
            </button>
          </div>
        </div>
      </header>

      <main className="privacy-main">
        <section className="privacy-hero animate-section">
          <div className="hero-content">
            <h2>Data Privacy & Disclaimer</h2>
            <p>Your privacy and data security are our top priorities at Taguig City University</p>
          </div>
        </section>

        <section className="privacy-section animate-section">
          <div className="privacy-content">
            <div className="privacy-section-header">
              <h3>Data Privacy Act Compliance</h3>
              <p>Protecting your personal information in accordance with Philippine law</p>
            </div>
            
            <div className="privacy-grid">
              <div className="privacy-card">
                <div className="privacy-icon">🔒</div>
                <h4>Data Privacy Act Compliance</h4>
                <p>
                  This platform fully complies with Republic Act No. 10173, also known as the Data Privacy Act of 2012. 
                  We are committed to protecting your personal information and ensuring its confidentiality, integrity, and availability.
                </p>
                <ul className="privacy-list">
                  <li>✓ Secure data encryption and storage</li>
                  <li>✓ Limited access to authorized personnel only</li>
                  <li>✓ Regular security audits and monitoring</li>
                  <li>✓ Compliance with NPC guidelines</li>
                </ul>
              </div>
              
              <div className="privacy-card">
                <div className="privacy-icon">📋</div>
                <h4>Information Collection</h4>
                <p>
                  We collect only necessary information required for the CEAA application process and academic services. 
                  This includes personal details, academic records, and supporting documents.
                </p>
                <ul className="privacy-list">
                  <li>✓ Personal identification information</li>
                  <li>✓ Academic records and grades</li>
                  <li>✓ Financial assistance documents</li>
                  <li>✓ Contact information for communication</li>
                </ul>
              </div>
              
              <div className="privacy-card">
                <div className="privacy-icon">🛡️</div>
                <h4>Your Rights</h4>
                <p>
                  As a data subject, you have the right to be informed, access your data, correct inaccuracies, 
                  erase or block your data, and file complaints with the National Privacy Commission.
                </p>
                <ul className="privacy-list">
                  <li>✓ Right to be informed about data processing</li>
                  <li>✓ Right to access your personal data</li>
                  <li>✓ Right to rectify inaccurate information</li>
                  <li>✓ Right to data portability and erasure</li>
                </ul>
              </div>
            </div>
            
            <div className="disclaimer-section">
              <h4>Important Disclaimer</h4>
              <div className="disclaimer-content">
                <p>
                  <strong>Educational Use:</strong> This TCU-CEAA Portal is designed exclusively for educational and administrative purposes 
                  related to the City Educational Assistance Allowance program of Taguig City University.
                </p>
                <p>
                  <strong>Accuracy of Information:</strong> While we strive to maintain accurate and up-to-date information, 
                  Taguig City University reserves the right to modify program requirements, eligibility criteria, and procedures 
                  without prior notice. Users are advised to verify critical information with university officials.
                </p>
                <p>
                  <strong>Technical Availability:</strong> The portal may experience temporary interruptions for maintenance or technical issues. 
                  TCU is not liable for any inconvenience caused by system downtime or technical difficulties.
                </p>
                <p>
                  <strong>User Responsibility:</strong> Users are responsible for providing accurate information and maintaining 
                  the confidentiality of their login credentials. Any misuse of the system may result in account suspension 
                  or termination of services.
                </p>
                <p>
                  <strong>External Links:</strong> This portal may contain links to external websites. TCU is not responsible 
                  for the content, privacy practices, or security of external sites.
                </p>
              </div>
              
              <div className="contact-dpo">
                <h5>Data Protection Officer Contact</h5>
                <p>
                  For data privacy concerns, complaints, or inquiries, please contact our Data Protection Officer:
                </p>
                <div className="dpo-details">
                  <p>📧 <strong>Email:</strong> dpo@tcu.edu.ph</p>
                  <p>📞 <strong>Phone:</strong> (02) 8837-8900 ext. 1234</p>
                  <p>📍 <strong>Office:</strong> Data Privacy Office, TCU Main Campus</p>
                </div>
              </div>
            </div>
            
            <div className="consent-notice">
              <div className="consent-icon">⚠️</div>
              <div className="consent-text">
                <p>
                  <strong>Consent Notice:</strong> By using this portal and submitting your information, you acknowledge that you have read, 
                  understood, and agree to our data privacy policy and the terms outlined in this disclaimer. 
                  Your continued use of this platform constitutes your consent to the collection, processing, 
                  and storage of your personal data as described herein.
                </p>
              </div>
            </div>

            <div className="additional-sections">
              <div className="data-retention">
                <h4>Data Retention Policy</h4>
                <p>
                  We retain your personal data only for as long as necessary to fulfill the purposes for which it was collected 
                  or as required by law. Academic records and CEAA application data are typically retained for a period of 
                  seven (7) years after graduation or program completion, unless otherwise required by university policies or legal obligations.
                </p>
              </div>

              <div className="third-party">
                <h4>Third-Party Services</h4>
                <p>
                  Our platform may integrate with authorized third-party services for enhanced functionality. 
                  These services are carefully vetted and bound by strict data protection agreements. 
                  We do not sell, trade, or rent your personal information to third parties for commercial purposes.
                </p>
              </div>

              <div className="security-measures">
                <h4>Security Measures</h4>
                <p>
                  We employ industry-standard security measures including SSL encryption, secure servers, 
                  regular security audits, and access controls to protect your personal information. 
                  However, no internet transmission is 100% secure, and we cannot guarantee absolute security.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="privacy-contact animate-section">
          <div className="contact-content">
            <h3>Have Questions About Privacy?</h3>
            <p>We're here to help with any privacy-related concerns or questions</p>
            <div className="contact-buttons">
              <button className="contact-btn primary" onClick={() => window.location.href = 'mailto:dpo@tcu.edu.ph'}>
                Contact Data Protection Officer
              </button>
              <button className="contact-btn secondary" onClick={onBackToHome}>
                Return to Homepage
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer className="privacy-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>TCU-CEAA Portal</h4>
            <p>Committed to protecting your privacy and ensuring data security in accordance with Philippine law.</p>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><button onClick={onBackToHome}>Back to Home</button></li>
              <li><a href="mailto:dpo@tcu.edu.ph">Contact DPO</a></li>
              <li><a href="https://privacy.gov.ph/" target="_blank" rel="noopener noreferrer">NPC Website</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Taguig City University CEAA Portal. All rights reserved.</p>
          <p>Data Privacy Act Compliant | Secure & Confidential</p>
        </div>
      </footer>

      {/* Scroll to Top Button */}
      {showScrollToTop && (
        <button 
          className="scroll-to-top-btn"
          onClick={scrollToTop}
          aria-label="Scroll to top"
        >
          <svg 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path 
              d="M12 8L6 14L7.41 15.41L12 10.83L16.59 15.41L18 14L12 8Z" 
              fill="currentColor"
            />
          </svg>
        </button>
      )}
    </div>
  );
};

export default Privacy;
