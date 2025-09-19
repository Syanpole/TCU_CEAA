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
  onPrivacyClick: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLoginClick, onRegisterClick, onPrivacyClick }) => {
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

    // Handle smooth scrolling for navigation links
    const handleNavClick = (e: Event) => {
      const target = e.target as HTMLAnchorElement;
      if (target.getAttribute('href')?.startsWith('#')) {
        e.preventDefault();
        const targetId = target.getAttribute('href')?.substring(1);
        const targetElement = document.getElementById(targetId!);
        if (targetElement) {
          const headerHeight = 100;
          const targetPosition = targetElement.offsetTop - headerHeight;
          window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
          });
        }
      }
    };

    // Add click listeners to navigation links
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    navLinks.forEach(link => {
      link.addEventListener('click', handleNavClick);
    });

    window.addEventListener('scroll', handleScroll);

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
      navLinks.forEach(link => {
        link.removeEventListener('click', handleNavClick);
      });
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
        {/* TCU-CEAA Banner Section */}
        <section className="banner-section animate-section">
          <div className="banner-container">
            <img 
              src="/images/tcu_ceaa_banner.jpg" 
              alt="TCU-CEAA Banner" 
              className="banner-image"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling?.classList.remove('hidden');
              }}
            />
            <div className="banner-fallback" style={{ display: 'none' }}>
              <div className="banner-logo-section">
                <img src="/images/TCU_logo.png" alt="TCU Logo" className="banner-logo" />
                <div className="banner-title-section">
                  <h1>TCU-CEAA</h1>
                  <h2>Computer Engineering Alumni Association</h2>
                </div>
              </div>
            </div>
            <div className="banner-overlay">
              <div className="banner-content">
                <h2>Welcome to TCU-CEAA Portal</h2>
                <p>Supporting Computer Engineering Students Through Academic Excellence</p>
              </div>
            </div>
          </div>
        </section>

        <section className="hero animate-section">
          <div className="hero-content">
            <div className="hero-text">
              <h1>Empowering Future Engineers</h1>
              <h2>TCU Computer Engineering Alumni Association</h2>
              <p>
                Join our community of successful Computer Engineering graduates and access 
                exclusive opportunities, scholarships, and career advancement programs designed 
                to help you excel in your academic and professional journey.
              </p>
              <div className="hero-buttons">
                <button className="cta-primary" onClick={handleLoginClick}>
                  Get Started Today
                </button>
                <button className="cta-secondary" onClick={handleRegisterClick}>
                  Join Our Community
                </button>
              </div>
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">500+</div>
                  <div className="stat-label">Alumni Members</div>
                </div>
                <div className="stat">
                  <div className="stat-number">₱2M+</div>
                  <div className="stat-label">Scholarships Awarded</div>
                </div>
                <div className="stat">
                  <div className="stat-number">95%</div>
                  <div className="stat-label">Success Rate</div>
                </div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="hero-stats-visual">
                <div className="visual-stat">
                  <div className="stat-icon">🎓</div>
                  <div className="stat-info">
                    <div className="big-number">1000+</div>
                    <div className="stat-desc">Graduates Supported</div>
                  </div>
                </div>
                <div className="visual-stat">
                  <div className="stat-icon">💼</div>
                  <div className="stat-info">
                    <div className="big-number">85%</div>
                    <div className="stat-desc">Job Placement Rate</div>
                  </div>
                </div>
                <div className="visual-stat">
                  <div className="stat-icon">🌟</div>
                  <div className="stat-info">
                    <div className="big-number">4.9/5</div>
                    <div className="stat-desc">Student Satisfaction</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="about" className="info-section animate-section">
          <div className="LandingPage-section-header">
            <h3>Why Choose TCU-CEAA?</h3>
            <p>Discover the benefits of joining our thriving alumni community</p>
          </div>
          <div className="info-grid">
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/financial-assistance.png" alt="Financial Assistance" />
              </div>
              <h4>Financial Support</h4>
              <p>Access scholarships, grants, and financial aid programs designed to help you succeed academically without financial stress.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/easy-application.png" alt="Easy Application" />
              </div>
              <h4>Easy Application</h4>
              <p>Streamlined application process with digital submissions and real-time status tracking for all your needs.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/quick-processing.png" alt="Quick Processing" />
              </div>
              <h4>Quick Processing</h4>
              <p>Fast and efficient processing of applications with transparent timelines and regular updates on your progress.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">
                <img src="/images/track-status.png" alt="Track Status" />
              </div>
              <h4>Track Status</h4>
              <p>Monitor your application status in real-time with detailed tracking and notification system.</p>
            </div>
          </div>
        </section>

        <section id="features" className="features-section animate-section">
          <div className="LandingPage-section-header">
            <h3>Comprehensive Student Support</h3>
            <p>Everything you need to succeed in your academic journey</p>
          </div>
          <div className="features-grid">
            <div className="feature-category">
              <h4>🎓 Academic Excellence</h4>
              <ul>
                <li>Merit-based scholarships and grants</li>
                <li>Academic performance incentives</li>
                <li>Research funding opportunities</li>
                <li>Study abroad program support</li>
                <li>Academic mentorship programs</li>
              </ul>
            </div>
            <div className="feature-category">
              <h4>💼 Career Development</h4>
              <ul>
                <li>Industry internship placements</li>
                <li>Professional networking events</li>
                <li>Career guidance and counseling</li>
                <li>Job placement assistance</li>
                <li>Professional skill development</li>
              </ul>
            </div>
            <div className="feature-category">
              <h4>🌟 Community Support</h4>
              <ul>
                <li>Alumni mentorship network</li>
                <li>Peer-to-peer learning groups</li>
                <li>Community service opportunities</li>
                <li>Leadership development programs</li>
                <li>Social and cultural activities</li>
              </ul>
            </div>
          </div>
        </section>

        <section id="process" className="landing-process-section animate-section">
          <div className="LandingPage-section-header">
            <h3>Simple Application Process</h3>
            <p>Get started in just a few easy steps</p>
          </div>
          <div className="landing-process-steps">
            <div className="landing-step">
              <div className="landing-step-number">1</div>
              <div className="landing-step-content">
                <h4>Register Account</h4>
                <p>Create your student account with basic information</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">2</div>
              <div className="landing-step-content">
                <h4>Complete Profile</h4>
                <p>Fill in your academic and personal details</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">3</div>
              <div className="landing-step-content">
                <h4>Submit Application</h4>
                <p>Choose your program and submit required documents</p>
              </div>
            </div>
            <div className="landing-step-arrow">→</div>
            <div className="landing-step">
              <div className="landing-step-number">4</div>
              <div className="landing-step-content">
                <h4>Get Approved</h4>
                <p>Track your application and receive your benefits</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section animate-section">
          <div className="cta-content">
            <h3>Ready to Transform Your Future?</h3>
            <p>Join thousands of successful Computer Engineering students who have benefited from our programs</p>
            <div className="cta-buttons-large">
              <button className="cta-primary-large" onClick={handleLoginClick}>
                Access Your Portal
              </button>
              <button className="cta-secondary-large" onClick={handleRegisterClick}>
                Start Your Journey
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer id="contact" className="landing-footer animate-section">
        <div className="footer-content">
          <div className="footer-section">
            <h4>TCU-CEAA Portal</h4>
            <p>
              Empowering Computer Engineering students through comprehensive support,
              scholarships, and community engagement since our founding.
            </p>
            <div className="social-links">
              <a href="https://www.facebook.com/TCUPhilippines" className="social-btn facebook">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a href="https://www.tcu.edu.ph" className="social-btn website">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </a>
            </div>
          </div>

          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#about">About Us</a></li>
              <li><a href="#features">Features</a></li>
              <li><a href="#process">Process</a></li>
              <li><button className="footer-link-button" onClick={showFAQ}>FAQ</button></li>
              <li><button className="footer-link-button" onClick={showHelpCenter}>Help Center</button></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Student Resources</h4>
            <ul>
              <li><a href="#">Scholarship Programs</a></li>
              <li><a href="#">Academic Support</a></li>
              <li><a href="#">Career Services</a></li>
              <li><a href="#">Alumni Network</a></li>
              <li><a href="#">Student Portal</a></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4>Legal & Support</h4>
            <ul>
              <li><button className="footer-link-button" onClick={showPrivacy}>Privacy Policy</button></li>
              <li><button className="footer-link-button" onClick={showDisclaimer}>Terms of Service</button></li>
              <li><a href="#">Contact Support</a></li>
              <li><a href="#">Report Issues</a></li>
              <li><a href="#">Accessibility</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2024 TCU Computer Engineering Alumni Association. All rights reserved.</p>
          <p>Tarlac College University - College of Engineering</p>
        </div>
      </footer>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <button className="scroll-to-top-btn" onClick={scrollToTop}>
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14l5-5 5 5z"/>
          </svg>
        </button>
      )}

      {/* Modals */}
      {showLoginModal && (
        <ModalLogin 
          onClose={closeModals}
          onSwitchToRegister={switchToRegister}
        />
      )}

      {showRegisterModal && (
        <ModalRegistration 
          onClose={closeModals}
          onSwitchToLogin={switchToLogin}
        />
      )}

      {showDisclaimerModal && (
        <DisclaimerModal onClose={closeModals} />
      )}

      {showPrivacyModal && (
        <PrivacyPolicyModal onClose={closeModals} />
      )}

      {showFAQModal && (
        <FAQModal onClose={closeModals} />
      )}

      {showHelpCenterModal && (
        <HelpCenterModal onClose={closeModals} />
      )}
    </div>
  );
};

export default LandingPage;