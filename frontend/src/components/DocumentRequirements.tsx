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
      title: "Junior High School Completion Certificate",
      description: "(for New Applicant)",
      required: true,
      forNewOnly: true
    },
    {
      id: 2,
      title: "Senior High School Diploma/Certification from Principal",
      description: "(for New Applicant)",
      required: true,
      forNewOnly: true
    },
    {
      id: 3,
      title: "School ID or any VALID Government-issued ID",
      description: "(back-to-back photocopy in a single page)",
      required: true,
      acceptableIds: [
        "e-Card/UMID Card", "Driver's License", "Passport", "SSS ID", "Voter's ID", "BIR (TIN ID)",
        "Pag-ibig ID", "PRC License", "Senior Citizen ID", "Company ID", "Postal ID", "PhilHealth ID",
        "Philippine Identification (PhilID/ePhilID)/National ID", "AFP Beneficiary/Dependent's ID"
      ]
    },
    {
      id: 4,
      title: "Proof that ONE of the parents is an active Taguig Voter",
      description: "",
      required: true
    },
    {
      id: 5,
      title: "Proof that applicant is an active Taguig Voter",
      description: "(if 18 years old and up)",
      required: false
    },
    {
      id: 6,
      title: "Birth Certificate",
      description: "",
      required: true
    }
  ];

  const otherNecessaryDocs = [
    {
      title: "Death Certificate (Parent)",
      description: "(if deceased)",
      required: false
    },
    {
      title: "ALS Certificate",
      description: "(in appropriate cases)",
      required: false
    },
    {
      title: "Others",
      description: "(as needed in some cases, like Form 137)",
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
        {/* Merit Incentive Section */}
        <div className="merit-incentive-section">
          <div className="section-header merit-header">
            <h2>🏆 MERIT INCENTIVE</h2>
          </div>
          <div className="merit-content">
            <p>
              The Ordinance also provides for a <strong>Merit Incentive of ₱5,000 per semester or ₱10,000 per year</strong>, 
              to qualified TCU students who, at the end of the semester, have a Grade Point Average (G.P.A.) of at least <strong>"1.75" or higher</strong>, 
              with at least <strong>15 credit units earned</strong>, with <strong>NO failing marks, incomplete, blank or no grade subjects, or dropped subjects</strong>.
            </p>
            <p className="merit-note">
              <strong>Note:</strong> Grades for P.E. & NSTP are not included in the computation. 
              This is to encourage diligent study and foster excellence among students.
            </p>
          </div>
        </div>

        {/* Documents to be Submitted Section */}
        <div className="requirements-section new-applicants">
          <div className="section-header">
            <h2>DOCUMENTS TO BE SUBMITTED</h2>
          </div>

          <div className="applicant-type-note">
            <div className="note-icon">⚠️</div>
            <div className="note-content">
              <strong>IMPORTANT:</strong> You will be checked if you are a <strong>NEW APPLICANT</strong> or <strong>RENEWING APPLICANT</strong>.
              <br/>
              For <strong>NEW APPLICANTS</strong>, you must submit <strong>at least 3 documents</strong>:
              <ul>
                <li>Junior High School (JHS) Report Card OR Senior High School (SHS) Report Card</li>
                <li>School ID or Valid Government-issued ID</li>
                <li>Birth Certificate</li>
              </ul>
            </div>
          </div>

          <div className="section-subheader">
            <h3>Checklist of documents needed to be submitted, after applying online, and on specified dates:</h3>
          </div>

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
