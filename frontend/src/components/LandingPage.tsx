import React, { useEffect } from 'react';
import './LandingPage.css';

interface LandingPageProps {
  onLoginClick: () => void;
  onRegisterClick: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLoginClick, onRegisterClick }) => {
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

    return () => observer.disconnect();
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
              TCU CEAA Portal
            </h1>
          </div>
          <nav className="nav-menu">
            <a href="#about">About</a>
            <a href="#features">Features</a>
            <a href="#process">Process</a>
            <a href="#contact">Contact</a>
          </nav>
          <div className="auth-buttons">
            <button className="signin-btn" onClick={onLoginClick}>
              Sign In
            </button>
            <button className="register-btn" onClick={onRegisterClick}>
              Student Registration
            </button>
          </div>
        </div>
      </header>

      <main className="landing-main">
        

        <section className="hero animate-section">
          <div className="hero-content">
            <div className="hero-text">
              <h2>Excellence in Academic Affairs</h2>
              <p>
                Welcome to the official portal of TCU Center for Excellence in Academic Affairs. 
                Experience seamless academic management, student services, and administrative 
                excellence powered by modern technology and AI-driven insights.
              </p>
              <div className="hero-buttons">
                <button className="cta-primary" onClick={onRegisterClick}>
                  Student Registration
                </button>
                <button className="cta-secondary" onClick={onLoginClick}>
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
            <div className="hero-visual">
              <div className="floating-card card-1">
                <div className="card-icon">
                  <img src="/images/energy-management.png" alt="Smart Management" />
                </div>
                <div className="card-text">Smart Management</div>
              </div>
              <div className="floating-card card-2">
                <div className="card-icon">
                  <img src="/images/performance.png" alt="Fast Processing" />
                </div>
                <div className="card-text">Fast Processing</div>
              </div>
              <div className="floating-card card-3">
                <div className="card-icon">
                  <img src="/images/academic-achievement.png" alt="Academic Excellence" />
                </div>
                <div className="card-text">Academic Excellence</div>
              </div>
              <div className="floating-card card-4">
                <div className="card-icon">
                  <img src="/images/data-analytics.png" alt="Data Analytics" />
                </div>
                <div className="card-text">Data Analytics</div>
              </div>
            </div>
          </div>
        </section>

        {/* TCU CEAA Banner Section */}
        <section className="banner-section animate-section">
          <div className="banner-container">
            {/* Full TCU CEAA Banner Image */}
            <img 
              src="/images/TCU-CEAA-IMAGE.jpg" 
              alt="Taguig City University - City Educational Assistance Allowance Program" 
              className="banner-image"
            />
          </div>
        </section>

        <section id="about" className="info-section animate-section">
          <div className="section-header">
            <h3>About TCU CEAA</h3>
            <p>Transforming academic excellence through innovative solutions</p>
          </div>
          <div className="info-grid">
            <div className="info-card">
              <div className="info-icon">🎓</div>
              <h4>Academic Excellence</h4>
              <p>Supporting outstanding academic programs with comprehensive management tools and data-driven insights.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">🤝</div>
              <h4>Student Services</h4>
              <p>Providing seamless student experience through integrated services and support systems.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">🌍</div>
              <h4>Innovation Hub</h4>
              <p>Leading educational innovation with cutting-edge technology and modern pedagogical approaches.</p>
            </div>
            <div className="info-card">
              <div className="info-icon">📈</div>
              <h4>Performance Analytics</h4>
              <p>Leveraging data analytics to enhance academic performance and institutional effectiveness.</p>
            </div>
          </div>
        </section>

        <section id="features" className="features-section animate-section">
          <div className="section-header">
            <h3>Platform Features</h3>
            <p>Discover what makes our platform exceptional</p>
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

        <section id="process" className="process-section animate-section">
          <div className="section-header">
            <h3>How It Works</h3>
            <p>Simple steps to access your academic portal</p>
          </div>
          <div className="process-steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h4>Create Account</h4>
                <p>Register with your student credentials</p>
              </div>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h4>Verify Identity</h4>
                <p>Complete account verification process</p>
              </div>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h4>Access Dashboard</h4>
                <p>Navigate your personalized portal</p>
              </div>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h4>Manage Academics</h4>
                <p>Handle all academic requirements</p>
              </div>
            </div>
          </div>
        </section>

        <section className="cta-section animate-section">
          <div className="cta-content">
            <h3>Ready to Get Started?</h3>
            <p>Join the TCU CEAA community and experience excellence in academic management</p>
            <div className="cta-buttons-large">
              <button className="cta-primary-large" onClick={onRegisterClick}>
                Student Registration
              </button>
              <button className="cta-secondary-large" onClick={onLoginClick}>
                Already Have Account? Sign In
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer id="contact" className="landing-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>TCU CEAA Portal</h4>
            <p>Center for Excellence in Academic Affairs - Leading innovation in education.</p>
            <div className="social-links">
              <button className="social-btn facebook" title="Facebook">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </button>
              <button className="social-btn twitter" title="Twitter">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </button>
              <button className="social-btn instagram" title="Instagram">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </button>
              <button className="social-btn linkedin" title="LinkedIn">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </button>
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
            <p>📍 Taguig City University<br />Taguig City, Philippines</p>
            <p>📞 (817) 257-TCU1 (8281)</p>
            <p>✉️ ceaa@tcu.edu</p>
          </div>
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li><a href="#faq">FAQ</a></li>
              <li><a href="#help">Help Center</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
              <li><a href="#terms">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Taguig City University CEAA Portal. All rights reserved.</p>
          <p>Powered by Modern Technology | Made with ❤️ for TCU Community</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;