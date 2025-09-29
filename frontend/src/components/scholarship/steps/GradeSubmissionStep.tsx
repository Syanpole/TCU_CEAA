import React, { useState } from 'react';
import { ScholarshipApplication } from '../../../types/scholarshipTypes';
import './GradeSubmissionStep.css';

interface GradeSubmissionStepProps {
  application: ScholarshipApplication;
  studentInfo: {
    studentId: string;
    studentName: string;
    yearLevel: string;
    program: string;
  };
  onComplete: () => void;
}

interface GradeEntry {
  subject: string;
  grade: number;
  units: number;
}

const GradeSubmissionStep: React.FC<GradeSubmissionStepProps> = ({
  application,
  studentInfo,
  onComplete
}) => {
  const [grades, setGrades] = useState<GradeEntry[]>([
    { subject: '', grade: 0, units: 0 }
  ]);
  const [gwa, setGwa] = useState<number>(0);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationComplete, setVerificationComplete] = useState(false);

  const addGradeEntry = () => {
    setGrades([...grades, { subject: '', grade: 0, units: 0 }]);
  };

  const removeGradeEntry = (index: number) => {
    setGrades(grades.filter((_, i) => i !== index));
    calculateGWA();
  };

  const updateGrade = (index: number, field: keyof GradeEntry, value: string | number) => {
    const updatedGrades = [...grades];
    updatedGrades[index] = { ...updatedGrades[index], [field]: value };
    setGrades(updatedGrades);
    calculateGWA();
  };

  const calculateGWA = () => {
    const validGrades = grades.filter(g => g.subject && g.grade > 0 && g.units > 0);
    if (validGrades.length === 0) return;

    const totalUnits = validGrades.reduce((sum, g) => sum + g.units, 0);
    const totalGradePoints = validGrades.reduce((sum, g) => sum + (g.grade * g.units), 0);
    const calculatedGwa = totalGradePoints / totalUnits;
    setGwa(Math.round(calculatedGwa * 100) / 100);
  };

  const handleSubmitGrades = () => {
    setIsVerifying(true);
    // Simulate verification
    setTimeout(() => {
      setIsVerifying(false);
      setVerificationComplete(true);
    }, 2000);
  };

  const handleContinue = () => {
    onComplete();
  };

  const isValidForSubmission = grades.some(g => g.subject && g.grade > 0 && g.units > 0);

  return (
    <div className="grade-submission-step">
      <div className="grade-content">
        <div className="grade-instructions">
          <h4>Grade Submission Instructions</h4>
          <ul>
            <li>Enter all your grades for the current semester</li>
            <li>Include subject name, grade, and units</li>
            <li>Grades will be verified against official records</li>
            <li>Merit scholarship requires minimum 85% GWA</li>
          </ul>
        </div>

        {!verificationComplete ? (
          <>
            <div className="grade-entries">
              <h4>Enter Your Grades</h4>
              {grades.map((grade, index) => (
                <div key={index} className="grade-entry">
                  <input
                    type="text"
                    placeholder="Subject Name"
                    value={grade.subject}
                    onChange={(e) => updateGrade(index, 'subject', e.target.value)}
                  />
                  <input
                    type="number"
                    placeholder="Grade"
                    min="65"
                    max="100"
                    value={grade.grade || ''}
                    onChange={(e) => updateGrade(index, 'grade', parseFloat(e.target.value) || 0)}
                  />
                  <input
                    type="number"
                    placeholder="Units"
                    min="1"
                    max="6"
                    value={grade.units || ''}
                    onChange={(e) => updateGrade(index, 'units', parseInt(e.target.value) || 0)}
                  />
                  {grades.length > 1 && (
                    <button 
                      className="remove-grade-btn" 
                      onClick={() => removeGradeEntry(index)}
                      title="Remove grade entry"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
              
              <button className="add-grade-btn" onClick={addGradeEntry}>
                + Add Another Subject
              </button>
            </div>

            <div className="gwa-calculator">
              <h4>Current GWA: {gwa > 0 ? gwa.toFixed(2) : 'N/A'}</h4>
              {gwa > 0 && (
                <p className={gwa >= 85 ? 'eligible' : 'not-eligible'}>
                  {gwa >= 85 ? 'Eligible for Merit Scholarship' : 'Below Merit Threshold (85% required)'}
                </p>
              )}
            </div>

            {!isVerifying ? (
              <button 
                className="submit-grades-btn" 
                onClick={handleSubmitGrades}
                disabled={!isValidForSubmission}
              >
                Submit Grades for Verification
              </button>
            ) : (
              <div className="verifying-status">
                <div className="verification-spinner"></div>
                <p>Verifying grades with official records...</p>
              </div>
            )}
          </>
        ) : (
          <div className="verification-complete">
            <div className="success-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4>Grades Verified Successfully</h4>
            <p>Your grades have been verified and GWA calculated</p>
            <div className="final-gwa">
              <strong>Final GWA: {gwa.toFixed(2)}</strong>
            </div>
            <button className="continue-btn" onClick={handleContinue}>
              Continue to Final Step
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GradeSubmissionStep;