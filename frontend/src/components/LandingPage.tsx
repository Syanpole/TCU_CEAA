import React, { useEffect, useState } from 'react';
import Modal from './Modal';
import ModalLogin from './ModalLogin';
import ModalRegistration from './ModalRegistration';
import DisclaimerModal from './DisclaimerModal';
import PrivacyPolicyModal from './PrivacyPolicyModal';
import FAQModal from './FAQModal';
import HelpCenterModal from './HelpCenterModal';
import './LandingPage.css';

interface LandingPageProps {
  onLoginClick: () => void;
  onRegisterClick: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLoginClick, onRegisterClick }) => {
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [showDisclaimerModal, setShowDisclaimerModal] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showFAQModal, setShowFAQModal] = useState(false);
  const [showHelpCenterModal, setShowHelpCenterModal] = useState(false);

  const handleLoginClick = () => {
    setShowLoginModal(true);
  };

  const handleRegisterClick = () => {
    setShowRegisterModal(true);
  };

  const closeModals = () => {
    setShowLoginModal(false);
    setShowRegisterModal(false);
    setShowDisclaimerModal(false);
    setShowPrivacyModal(false);
    setShowFAQModal(false);
    setShowHelpCenterModal(false);
  };

  const showDisclaimer = () => {
    setShowDisclaimerModal(true);
  };

  const showPrivacy = () => {
    setShowPrivacyModal(true);
  };

  const showFAQ = () => {
    setShowFAQModal(true);
  };

  const showHelpCenter = () => {
    setShowHelpCenterModal(true);
  };

  const switchToLogin = () => {
    setShowRegisterModal(false);
    setShowLoginModal(true);
  };

  const switchToRegister = () => {
    setShowLoginModal(false);
    setShowRegisterModal(true);
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  useEffect(() => {
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
      setShowScrollTop(scrollTop > 300);
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);
  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">
              <img src="/images/TCU_logo.png" alt="TCU Logo" className="logo-image" />
            </div>
            <h1 
              className="clickable-title" 
              onClick={() => window.location.reload()}
              style={{ cursor: 'pointer', userSelect: 'none' }}
            >
              TCU-CEAA Portal
            </h1>
          </div>
          <nav className="nav-menu">
            <a href="#about">About</a>
            <a href="#features">Features</a>
            <a href="#process">Process</a>
            <a href="#contact">Contact</a>
          </nav>
          <div className="auth-buttons">
            <button className="signin-btn" onClick={handleLoginClick}>
              Sign In
            </button>
            <button className="register-btn" onClick={handleRegisterClick}>
              Student Registration
            </button>
          </div>
        </div>
      </header>

      <main className="landing-main">
        

        <section className="hero animate-section">
          <div className="hero-content">
            <div className="hero-text">
              <h2>City Educational Assistance Allowance</h2>
              <p>
                Welcome to the official portal of TCU City Educational Assistance Allowance. 
                Experience seamless academic management, student services, and administrative 
                excellence powered by modern technology and AI-driven insights.
              </p>
              <div className="hero-buttons">
                <button className="cta-primary" onClick={handleRegisterClick}>
                  Student Registration
                </button>
                <button className="cta-secondary" onClick={handleLoginClick}>
                  Sign In
                </button>
              </div>
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">5,000+</div>
                  <div className="stat-label">Active Students</div>
                </div>
                <div className="stat">
                  <div className="stat-number">98%</div>
                  <div className="stat-label">Satisfaction Rate</div>
                </div>
                <div className="stat">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">Support Available</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* TCU-CEAA Banner Section */}
        <section className="banner-section animate-section">
          <div className="banner-container">
            {/* Full TCU-CEAA Banner Image */}
            <img 
              src="/images/TCU-CEAA-IMAGE.jpg" 
              alt="Taguig City University - City Educational Assistance Allowance Program" 
              className="banner-image"
            />
          </div>
        </section>

        <section id="about" className="info-section animate-section">
          <div className="LandingPage-section-header">
            <h3>About TCU-CEAA</h3>
            <p>Supporting TCU students with educational financial assistance</p>
          </div>
          <div className="info-grid">
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/financial-assistance.png" alt="Financial Assistance" />
              </div>
              <h4>Financial Assistance</h4>
              <p>Get the financial support you need to continue your education and achieve your academic goals.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/easy-application.png" alt="Easy Application" />
              </div>
              <h4>Easy Application</h4>
              <p>Simple online application process - upload your documents and submit your grades easily.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/quick-processing.png" alt="Quick Processing" />
              </div>
              <h4>Quick Processing</h4>
              <p>Fast evaluation of your application so you can get your allowance as soon as possible.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/track-status.png" alt="Track Status" />
              </div>
              <h4>Track Status</h4>
              <p>Check your application status anytime, anywhere through your student dashboard.</p>
            </div>
          </div>
        </section>

        <section id="features" className="features-section animate-section">
          <div className="LandingPage-section-header">
            <h3>What You Can Do</h3>
            <p>Everything you need to apply for and manage your educational allowance</p>
          </div>
          <div className="features-grid">
            <div className="feature-category">
              <h4>Core Features</h4>
              <ul>
                <li>✅ Student Information System</li>
                <li>✅ Academic Records Management</li>
                <li>✅ Course Registration Portal</li>
                <li>✅ Grade Management System</li>
                <li>✅ Real-time Notifications</li>
              </ul>
            </div>
            <div className="feature-category">
              <h4>Advanced Capabilities</h4>
              <ul>
                <li>✅ AI-Powered Analytics</li>
                <li>✅ Mobile-Responsive Design</li>
                <li>✅ Secure Data Management</li>
                <li>✅ Integration APIs</li>
                <li>✅ Custom Reporting Tools</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="process" className="landing-process-section animate-section">
          <div className="LandingPage-section-header">
            <h3>How to Apply</h3>
            <p>Simple steps to get your educational allowance</p>
          </div>
          <div className="landing-process-steps">
            <div className="landing-step">
              <div className="landing-step-number">1</div>
              <div className="landing-step-content">
                <h4>Register Account</h4>
                <p>Sign up with your student information</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">2</div>
              <div className="landing-step-content">
                <h4>Submit Documents</h4>
                <p>Upload required documents and grades</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">3</div>
              <div className="landing-step-content">
                <h4>Access Dashboard</h4>
                <p>Navigate your personalized portal</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">4</div>
              <div className="landing-step-content">
                <h4>Get Allowance</h4>
                <p>Receive your educational assistance</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section animate-section">
          <div className="cta-content">
            <h3>Need Financial Support for Your Studies?</h3>
            <p>Join thousands of TCU students who are getting educational assistance through our program</p>
            <div className="cta-buttons-large">
              <button className="cta-primary-large" onClick={handleRegisterClick}>
                Apply for Allowance
              </button>
              <button className="cta-secondary-large" onClick={handleLoginClick}>
                Already Registered? Sign In
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer id="contact" className="landing-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>TCU-CEAA Portal</h4>
            <p>Taguig City University - City Educational Assistance Allowance - Supporting students through financial assistance and academic excellence.</p>
            <div className="social-links">
              <a 
                href="https://www.facebook.com/TaguigCityUniversity" 
                className="social-btn facebook" 
                title="Follow us on Facebook"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Visit our Facebook page (opens in new tab)"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a 
                href="https://tcu.edu.ph/" 
                className="social-btn website" 
                title="Visit TCU Main Website"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Visit TCU main website (opens in new tab)"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zM4 12c0-.61.08-1.21.22-1.79L9 15v1c0 1.1.9 2 2 2v1.93C7.06 19.43 4 16.07 4 12zm13.89 5.4c-.26-.81-1-1.4-1.89-1.4h-1v-3c0-.55-.45-1-1-1h-6v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41C17.92 5.77 20 8.65 20 12c0 2.08-.81 3.98-2.11 5.4z"/>
                </svg>
              </a>
              <a 
                href="https://www.linkedin.com/school/taguig-city-university-graduateschool/posts/?feedView=all"
                className="social-btn linkedin" 
                title="Connect with us on LinkedIn"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Visit our LinkedIn page (opens in new tab)"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
            </div>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#about">About CEAA</a></li>
              <li><a href="#features">Features</a></li>
              <li><a href="#process">How It Works</a></li>
              <li><a href="#contact">Contact Support</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Contact Info</h4>
            <p>📍 Gen. Santos Ave. Central Bicutan<br />Taguig City, Philippines</p>
            <p>📞 (817) 257-TCU1 (8281)</p>
            <p>✉️ ceaa@tcu.edu</p>
          </div>
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li><button onClick={showFAQ} className="footer-link-button">FAQ</button></li>
              <li><button onClick={showHelpCenter} className="footer-link-button">Help Center</button></li>
              <li><button onClick={showPrivacy} className="footer-link-button">Privacy Policy</button></li>
              <li><button onClick={showDisclaimer} className="footer-link-button">Disclaimer</button></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Taguig City University CEAA Portal. All rights reserved.</p>
          <p>Powered by Modern Technology | Made with ❤️ for TCU Community</p>
        </div>
      </footer>

      {/* Scroll to Top Button */}
      <button 
        className={`scroll-to-top ${showScrollTop ? 'visible' : ''}`}
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
            d="M12 19V5M5 12L12 5L19 12" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* Modals */}
      <Modal
        isOpen={showLoginModal}
        onClose={closeModals}
        size="small"
      >
        <ModalLogin
          onClose={closeModals}
          onSwitchToRegister={switchToRegister}
        />
      </Modal>

      <Modal
        isOpen={showRegisterModal}
        onClose={closeModals}
        size="medium"
      >
        <ModalRegistration
          onClose={closeModals}
          onSwitchToLogin={switchToLogin}
        />
      </Modal>

      <Modal
        isOpen={showDisclaimerModal}
        onClose={closeModals}
        size="large"
      >
        <DisclaimerModal onClose={closeModals} />
      </Modal>

      <Modal
        isOpen={showPrivacyModal}
        onClose={closeModals}
        size="large"
      >
        <PrivacyPolicyModal onClose={closeModals} />
      </Modal>

      <Modal
        isOpen={showFAQModal}
        onClose={closeModals}
        size="large"
      >
        <FAQModal onClose={closeModals} />
      </Modal>

      <Modal
        isOpen={showHelpCenterModal}
        onClose={closeModals}
        size="large"
      >
        <HelpCenterModal onClose={closeModals} />
      </Modal>
    </div>
  );
};

export default LandingPage;