import React, { useEffect, useState } from 'react';
import './FAQ.css';

interface FAQProps {
  onBackToHome: () => void;
}

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

const FAQ: React.FC<FAQProps> = ({ onBackToHome }) => {
  const [showScrollToTop, setShowScrollToTop] = useState(false);
  const [activeCategory, setActiveCategory] = useState('all');
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const faqData: FAQItem[] = [
    // General Questions
    {
      category: 'general',
      question: 'What is the City Educational Assistance Allowance (CEAA)?',
      answer: 'The City Educational Assistance Allowance (CEAA) is a scholarship program provided by Taguig City Government to help qualified Taguig City University students with their educational expenses. It provides financial assistance to deserving students based on academic performance and financial need.'
    },
    {
      category: 'general',
      question: 'Who is eligible for CEAA?',
      answer: 'To be eligible for CEAA, you must be: (1) A bonafide resident of Taguig City, (2) Currently enrolled at Taguig City University, (3) Meet the minimum GPA requirements, (4) In good academic standing, and (5) Meet the financial need criteria set by the university.'
    },
    {
      category: 'general',
      question: 'How much is the CEAA scholarship grant?',
      answer: 'The CEAA scholarship amount varies depending on the program and availability of funds. It typically covers partial to full tuition fees and may include allowances for books and other educational expenses. Please check with the CEAA office for current scholarship amounts.'
    },
    // Application Process
    {
      category: 'application',
      question: 'How do I apply for CEAA?',
      answer: 'You can apply for CEAA through this online portal. Create an account, complete the application form, upload all required documents, and submit your application. You will receive notifications about your application status via email and through the portal.'
    },
    {
      category: 'application',
      question: 'What documents do I need to submit?',
      answer: 'Required documents typically include: (1) Certificate of Residency from Barangay, (2) Certificate of Grades/Transcript of Records, (3) Valid ID, (4) Proof of enrollment/Registration Form, (5) Income tax return or Certificate of Indigency, and (6) Birth Certificate. Additional documents may be required depending on your situation.'
    },
    {
      category: 'application',
      question: 'When is the application deadline?',
      answer: 'Application deadlines vary per semester. Generally, applications open at the beginning of each semester and close 2-3 weeks before the start of classes. Please check the portal announcements and your student email for specific deadlines.'
    },
    {
      category: 'application',
      question: 'Can I edit my application after submission?',
      answer: 'Once submitted, applications cannot be edited. However, if you need to make corrections, you can contact the CEAA office immediately after submission. For future applications, please review all information carefully before submitting.'
    },
    // Technical Support
    {
      category: 'technical',
      question: 'I forgot my password. How can I reset it?',
      answer: 'Click on the "Forgot Password" link on the login page. Enter your registered email address, and you will receive a password reset link. Follow the instructions in the email to create a new password.'
    },
    {
      category: 'technical',
      question: 'Why can\'t I upload my documents?',
      answer: 'Common reasons include: (1) File size too large (max 5MB per file), (2) Unsupported file format (use PDF, JPG, or PNG), (3) Poor internet connection, or (4) Browser issues. Try using a different browser or clearing your cache. If the problem persists, contact technical support.'
    },
    {
      category: 'technical',
      question: 'Is the portal mobile-friendly?',
      answer: 'Yes! The TCU-CEAA Portal is fully responsive and works on smartphones, tablets, and desktop computers. You can access all features from any device with an internet connection.'
    },
    {
      category: 'technical',
      question: 'What browsers are supported?',
      answer: 'The portal works best with the latest versions of Google Chrome, Mozilla Firefox, Microsoft Edge, and Safari. We recommend keeping your browser updated for the best experience and security.'
    },
    // Account & Security
    {
      category: 'account',
      question: 'How do I create an account?',
      answer: 'Click on "Register" from the homepage. Fill in your personal information, student ID, TCU email address, and create a strong password. You will receive a verification email. Click the verification link to activate your account.'
    },
    {
      category: 'account',
      question: 'Is my personal information secure?',
      answer: 'Yes. We implement industry-standard security measures including SSL encryption, secure servers, and strict access controls. All data is protected in compliance with the Data Privacy Act of 2012 (RA 10173). For more information, please read our Privacy Policy.'
    },
    {
      category: 'account',
      question: 'Can I have multiple accounts?',
      answer: 'No. Each student is allowed only one account linked to their student ID and TCU email address. Creating multiple accounts may result in disqualification from the CEAA program.'
    },
    // Status & Notifications
    {
      category: 'status',
      question: 'How do I check my application status?',
      answer: 'Log in to your account and navigate to the "My Applications" section. You can view the current status of all your applications. You will also receive email notifications when your status changes.'
    },
    {
      category: 'status',
      question: 'What do the different application statuses mean?',
      answer: 'Pending: Application received and under review. In Review: Being evaluated by the CEAA committee. Approved: Application accepted, grant will be released. Rejected: Application not approved (you will receive feedback). Incomplete: Missing documents or information required.'
    },
    {
      category: 'status',
      question: 'How long does the review process take?',
      answer: 'The review process typically takes 2-4 weeks from the application deadline. During peak periods, it may take longer. You will be notified of any status changes via email and through the portal.'
    },
    // Disbursement
    {
      category: 'disbursement',
      question: 'When will I receive my scholarship grant?',
      answer: 'Once approved, scholarship grants are typically disbursed within 2-3 weeks. The exact timeline depends on the university\'s disbursement schedule and budget availability. You will be notified when your grant is ready for claiming.'
    },
    {
      category: 'disbursement',
      question: 'How will I receive the scholarship money?',
      answer: 'Scholarships may be disbursed through: (1) Direct application to your tuition fees, (2) Bank transfer to your registered account, or (3) Check pick-up at the CEAA office. The disbursement method will be specified in your approval notice.'
    }
  ];

  const categories = [
    { id: 'all', label: 'All Questions', icon: '📚' },
    { id: 'general', label: 'General', icon: '❓' },
    { id: 'application', label: 'Application', icon: '📝' },
    { id: 'technical', label: 'Technical', icon: '💻' },
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'status', label: 'Status', icon: '📊' },
    { id: 'disbursement', label: 'Disbursement', icon: '💰' }
  ];

  useEffect(() => {
    window.scrollTo(0, 0);

    const handleScroll = () => {
      setShowScrollToTop(window.pageYOffset > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const filteredFAQs = faqData.filter(faq => {
    const matchesCategory = activeCategory === 'all' || faq.category === activeCategory;
    const matchesSearch = searchQuery === '' || 
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const toggleFAQ = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="faq-container">
      <header className="faq-header">
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

      <main className="faq-main">
        <section className="faq-hero">
          <div className="hero-content">
            <h2>Frequently Asked Questions</h2>
            <p>Find answers to common questions about the CEAA program</p>
            
            <div className="search-box">
              <svg className="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <input
                type="text"
                placeholder="Search for answers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
            </div>
          </div>
        </section>

        <section className="faq-categories">
          <div className="categories-container">
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`category-btn ${activeCategory === cat.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.id)}
              >
                <span className="category-icon">{cat.icon}</span>
                <span className="category-label">{cat.label}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="faq-content">
          <div className="faq-list">
            {filteredFAQs.length > 0 ? (
              filteredFAQs.map((faq, index) => (
                <div key={index} className={`faq-item ${expandedIndex === index ? 'expanded' : ''}`}>
                  <button className="faq-question" onClick={() => toggleFAQ(index)}>
                    <span>{faq.question}</span>
                    <svg 
                      className="faq-icon" 
                      width="24" 
                      height="24" 
                      viewBox="0 0 24 24" 
                      fill="none"
                    >
                      <path 
                        d="M6 9l6 6 6-6" 
                        stroke="currentColor" 
                        strokeWidth="2" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </button>
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-results">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2"/>
                  <path d="M32 20v16M32 44h.02" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <p>No questions found matching your search.</p>
                <button onClick={() => { setSearchQuery(''); setActiveCategory('all'); }}>
                  Clear filters
                </button>
              </div>
            )}
          </div>
        </section>

        <section className="faq-contact">
          <div className="contact-card">
            <h3>Still have questions?</h3>
            <p>Can't find the answer you're looking for? Our support team is here to help.</p>
            <div className="contact-actions">
              <a href="mailto:ceaa@tcu.edu.ph" className="contact-btn primary">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M3 4h14a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M2 5l8 5 8-5" stroke="currentColor" strokeWidth="2"/>
                </svg>
                Email Support
              </a>
              <a href="https://scholar.taguig.gov.ph/tcu" target="_blank" rel="noopener noreferrer" className="contact-btn secondary">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2"/>
                  <path d="M10 2a8 8 0 0 0 0 16M10 2a8 8 0 0 1 0 16M2 10h16" stroke="currentColor" strokeWidth="2"/>
                </svg>
                Visit TCU Website
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="faq-footer">
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

export default FAQ;
