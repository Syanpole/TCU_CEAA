import React, { useState } from 'react';
import './HelpModal.css';

interface FAQModalProps {
  onClose: () => void;
}

interface FAQItem {
  id: number;
  question: string;
  answer: string;
  category: string;
}

const FAQModal: React.FC<FAQModalProps> = ({ onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [expandedItems, setExpandedItems] = useState<number[]>([]);

  const faqData: FAQItem[] = [
    {
      id: 1,
      category: "Eligibility",
      question: "Who is eligible for the TCU-CEAA program?",
      answer: "The TCU-CEAA program is available to currently enrolled students at Taguig City University who meet the following criteria: (1) Must be a bona fide resident of Taguig City, (2) Enrolled in a degree program at TCU, (3) Maintaining satisfactory academic standing, (4) Meeting the financial need requirements as determined by the program guidelines."
    },
    {
      id: 2,
      category: "Application",
      question: "How do I apply for educational assistance?",
      answer: "To apply: (1) Register for an account on the TCU-CEAA Portal, (2) Complete your profile with accurate information, (3) Upload required documents (ID, enrollment certificate, grades, proof of residency), (4) Submit your application through the portal, (5) Wait for application review and approval notification."
    },
    {
      id: 3,
      category: "Documents",
      question: "What documents do I need to submit?",
      answer: "Required documents include: (1) Valid ID with photo, (2) Certificate of enrollment or registration, (3) Latest grades or transcript of records, (4) Proof of Taguig City residency (barangay certificate, utility bill, etc.), (5) Birth certificate, (6) Income certification (if applicable), (7) Any additional documents as requested by the office."
    },
    {
      id: 4,
      category: "Timeline",
      question: "How long does the application process take?",
      answer: "The application review typically takes 5-10 business days after submission of complete requirements. Processing time may vary depending on the volume of applications and completeness of submitted documents. You will receive email notifications about your application status updates."
    },
    {
      id: 5,
      category: "Payment",
      question: "How and when will I receive my allowance?",
      answer: "Once approved, allowances are typically disbursed monthly through the university's financial office. You may choose to receive payments through bank transfer or cash pickup at the designated office. Disbursement schedules are announced at the beginning of each semester."
    },
    {
      id: 6,
      category: "Academic",
      question: "What academic requirements must I maintain?",
      answer: "To continue receiving assistance, you must: (1) Maintain at least a 2.5 GPA or equivalent, (2) Complete required number of units per semester, (3) Submit grades at the end of each semester, (4) Remain in good academic standing with no major disciplinary actions, (5) Notify the office of any changes in enrollment status."
    },
    {
      id: 7,
      category: "Technical",
      question: "I'm having trouble accessing my account. What should I do?",
      answer: "If you're experiencing login issues: (1) Check that you're using the correct email and password, (2) Try resetting your password using the 'Forgot Password' link, (3) Clear your browser cache and cookies, (4) Try accessing from a different browser or device, (5) Contact technical support if the problem persists."
    },
    {
      id: 8,
      category: "Application",
      question: "Can I edit my application after submission?",
      answer: "Once submitted, applications cannot be directly edited by students. However, you can contact the CEAA office to request updates or corrections to your submitted information. It's important to review all information carefully before submission to avoid delays."
    },
    {
      id: 9,
      category: "Eligibility",
      question: "Can graduate students apply for CEAA?",
      answer: "Yes, graduate students enrolled in master's or doctoral programs at TCU are eligible to apply for educational assistance, provided they meet all other eligibility requirements including residency and academic standing criteria."
    },
    {
      id: 10,
      category: "Payment",
      question: "What happens if I don't receive my allowance on time?",
      answer: "If you don't receive your allowance by the expected date: (1) Check your application status on the portal, (2) Verify your contact information is up to date, (3) Contact the CEAA office directly, (4) Ensure all required documents are still valid and submitted, (5) Check for any pending requirements or communications."
    },
    {
      id: 11,
      category: "Academic",
      question: "What if my grades drop below the required GPA?",
      answer: "If your GPA falls below requirements: (1) You'll receive a warning notification, (2) You may be given a probationary period to improve grades, (3) Assistance may be temporarily suspended, (4) You can reapply once academic standing is restored, (5) Academic counseling resources may be provided to help you succeed."
    },
    {
      id: 12,
      category: "Technical",
      question: "How do I upload documents to the portal?",
      answer: "To upload documents: (1) Log into your account and go to the Documents section, (2) Click 'Upload New Document', (3) Select the document type from the dropdown, (4) Choose your file (PDF, JPG, PNG formats accepted), (5) Ensure file size is under 5MB, (6) Add a description if needed, (7) Click 'Upload' and wait for confirmation."
    }
  ];

  const categories = ['All', ...Array.from(new Set(faqData.map(item => item.category)))];

  const filteredFAQs = faqData.filter(item => {
    const matchesSearch = item.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.answer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const toggleExpanded = (id: number) => {
    setExpandedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="help-modal-container">
      <div className="help-modal-header">
        <h2>Frequently Asked Questions</h2>
        <p>Find answers to common questions about the TCU-CEAA program</p>
      </div>
      
      <div className="help-modal-search">
        <div className="search-bar">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          <input
            type="text"
            placeholder="Search frequently asked questions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="category-filter">
          {categories.map(category => (
            <button
              key={category}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="help-modal-content">
        {filteredFAQs.length > 0 ? (
          <div className="faq-list">
            {filteredFAQs.map(item => (
              <div key={item.id} className="faq-item">
                <button
                  className="faq-question"
                  onClick={() => toggleExpanded(item.id)}
                >
                  <span className="category-tag">{item.category}</span>
                  <span className="question-text">{item.question}</span>
                  <svg 
                    className={`expand-icon ${expandedItems.includes(item.id) ? 'expanded' : ''}`}
                    viewBox="0 0 24 24" 
                    fill="none" 
                    stroke="currentColor"
                  >
                    <polyline points="6,9 12,15 18,9"/>
                  </svg>
                </button>
                {expandedItems.includes(item.id) && (
                  <div className="faq-answer">
                    <p>{item.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results">
            <p>No questions found matching your search criteria.</p>
            <button onClick={() => {setSearchTerm(''); setSelectedCategory('All');}}>
              Clear filters
            </button>
          </div>
        )}
      </div>

      <div className="help-modal-actions">
        <div className="contact-info">
          <p>Can't find what you're looking for?</p>
          <p>Contact us at <strong>ceaa@tcu.edu.ph</strong> or <strong>(817) 257-8281</strong></p>
        </div>
        <button className="help-close-button" onClick={onClose}>
          Close FAQ
        </button>
      </div>
    </div>
  );
};

export default FAQModal;