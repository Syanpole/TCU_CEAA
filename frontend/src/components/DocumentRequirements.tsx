import React from 'react';
import { RequirementsIcon } from './Icons';
import './DocumentRequirements.css';

interface DocumentRequirementsProps {
  darkMode?: boolean;
}

const DocumentRequirements: React.FC<DocumentRequirementsProps> = ({ darkMode = false }) => {
  const newApplicantDocs = [
    {
      id: 1,
      title: "Junior High School Certificate/Grade 10 Report Card/Certification from Principal",
      description: "of the school that the applicant graduated from",
      required: true
    },
    {
      id: 2,
      title: "Senior High School Diploma/Grade 12 Report Card/Certification from Principal",
      description: "of the school that the applicant graduated from",
      required: true
    },
    {
      id: 3,
      title: "School ID or any VALID Government-issued ID",
      description: "(within the validity period, photocopied back-to-back on a single page)",
      required: true,
      acceptableIds: [
        "e-Card/UMID Card", "Driver's License", "Passport", "SSS ID", "Voter's ID", "BIR (TIN ID)",
        "Pag-ibig ID", "PRC License", "Senior Citizen ID", "Company ID", "Postal ID", "PhilHealth ID",
        "Philippine Identification (PhilID/ePhilID)/National ID", "AFP Beneficiary/Dependent's ID"
      ]
    },
    {
      id: 4,
      title: "Birth Certificate",
      description: "(issued by PSA/NSO/Civil Registry Office)",
      required: true
    }
  ];

  const otherNecessaryDocs = [
    {
      title: "Certified True Copy of Elementary and/or High School Form 137",
      description: "(for those who took but did not complete their Junior High School in Taguig or nearby and contiguous LGU in Metro Manila but graduated Senior High School in Taguig or nearby and contiguous LGU in Metro Manila)",
      required: false
    },
    {
      title: "ALS Certificate",
      description: "(if ALS Graduate)",
      required: false
    },
    {
      title: "Death Certificate",
      description: "(Parents, if claimed to be deceased, issued by PSA/NSO/Civil Registry Office)",
      required: false
    },
    {
      title: "Work Contract/VISA/Passport",
      description: "(if any of both parents are OFWs)",
      required: false
    },
    {
      title: "Original copy and one (1) photocopy of Comelec Stub",
      description: "issued after May 2022 Elections (for applicants and/or their parents who are newly registered or those who have applied for reactivation)",
      required: false
    }
  ];

  return (
    <div className={`document-requirements ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="announcement-header">
        <h1>ANNOUNCEMENT</h1>
        <div className="header-decoration">
          <div className="circle white"></div>
          <div className="circle red"></div>
          <div className="circle yellow"></div>
          <div className="circle white"></div>
        </div>
      </div>

      <div className="requirements-content">
        <div className="requirements-section new-applicants">
          <div className="section-header">
            <h2>REQUIREMENTS TO BE SUBMITTED <span className="subtitle">(FOR NEW APPLICANTS)</span></h2>
          </div>

          <div className="preparation-note">
            <p><strong>Prepare TWO (2) SETS:</strong></p>
            <p><strong>SET 1</strong> (all photocopies) - to be submitted to Taguig Scholarship Office</p>
            <p><strong>SET 2</strong> (original copies) - for verification</p>
          </div>

          <div className="document-order-note">
            <div className="note-icon">
              <RequirementsIcon size={24} />
            </div>
            <p><em>Please arrange the documents in this order:</em></p>
          </div>

          <div className="documents-list">
            {newApplicantDocs.map((doc) => (
              <div key={doc.id} className="document-item">
                <div className="doc-number">{doc.id}.</div>
                <div className="doc-content">
                  <h3>{doc.title}</h3>
                  <p className="doc-description">{doc.description}</p>
                  {doc.acceptableIds && (
                    <div className="acceptable-ids">
                      <p><strong>List of acceptable IDs:</strong></p>
                      <div className="ids-grid">
                        {doc.acceptableIds.map((id, index) => (
                          <span key={index} className="id-item">• {id}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="other-documents-section">
          <h3>Other necessary documents:</h3>
          <div className="other-docs-list">
            {otherNecessaryDocs.map((doc, index) => (
              <div key={index} className="other-doc-item">
                <div className="bullet">•</div>
                <div className="other-doc-content">
                  <h4>{doc.title}</h4>
                  <p className="other-doc-description">{doc.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="renewing-section">
          <div className="renewing-header">
            <h2>&gt;&gt;&gt; FOR RENEWING APPLICANTS</h2>
          </div>
          <div className="renewing-content">
            <h3>YOU DO NOT NEED TO SUBMIT YOUR REQUIREMENTS.</h3>
            <p>All qualified applicants will receive <strong>NOTICES</strong> containing the complete information about the schedule of the releasing of Scholarship Allowance.</p>
            
            <div className="distribution-note">
              <p>On the date of the distribution, make sure to bring your <strong>School ID</strong> along with its <strong>two (2) photocopies</strong> <em>(printed back-to-back on a single page bearing your signature over printed name)</em>.</p>
            </div>
          </div>
        </div>

        <div className="footer-section">
          <div className="motto">
            <em>"Investing in Education is Investing in the City's Foundation"</em>
          </div>
          <div className="contact-info">
            <div className="contact-item">
              <span className="icon">📘</span>
              <span>/taguigcity</span>
            </div>
            <div className="contact-item">
              <span className="icon">📷</span>
              <span>@taguigcity</span>
            </div>
            <div className="contact-item">
              <span className="icon">🐦</span>
              <span>@loveTagui g1</span>
            </div>
            <div className="contact-item">
              <span className="icon">🌐</span>
              <span>www.taguig.gov.ph</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentRequirements;
