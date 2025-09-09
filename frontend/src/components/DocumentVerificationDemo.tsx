import React, { useState } from 'react';
import './DocumentVerificationDemo.css';

interface VerificationResult {
  isValid: boolean;
  confidence: number;
  extractedData: Record<string, any>;
  issues: string[];
}

interface DocumentVerificationDemoProps {
  documentType: 'birth_certificate' | 'id' | 'coe' | 'grade' | 'voters_certificate';
  imageData?: string;
  onVerificationComplete?: (result: VerificationResult) => void;
}

const DocumentVerificationDemo: React.FC<DocumentVerificationDemoProps> = ({
  documentType,
  imageData,
  onVerificationComplete
}) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const simulateVerification = async () => {
    setIsVerifying(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Mock verification result based on document type
    const mockResult: VerificationResult = {
      isValid: Math.random() > 0.3, // 70% chance of being valid
      confidence: Math.round((Math.random() * 0.4 + 0.6) * 100), // 60-100% confidence
      extractedData: getMockExtractedData(documentType),
      issues: getMockIssues(documentType)
    };
    
    setVerificationResult(mockResult);
    setIsVerifying(false);
    
    if (onVerificationComplete) {
      onVerificationComplete(mockResult);
    }
  };

  const getMockExtractedData = (type: string): Record<string, any> => {
    const baseData = {
      birth_certificate: {
        fullName: "Juan Dela Cruz",
        dateOfBirth: "1995-06-15",
        placeOfBirth: "Manila, Philippines",
        registryNumber: "2023-1234567"
      },
      id: {
        fullName: "Maria Santos",
        idNumber: "1234-5678-9012",
        expiryDate: "2025-12-31",
        address: "123 Rizal St, Quezon City"
      },
      coe: {
        studentName: "Pedro Garcia",
        studentId: "2021-12345",
        program: "Bachelor of Science in Computer Science",
        yearLevel: "4th Year"
      },
      grade: {
        studentName: "Ana Lopez",
        studentId: "2020-67890",
        subject: "Mathematics 101",
        grade: "A",
        semester: "1st Semester AY 2023-2024"
      },
      voters_certificate: {
        voterName: "Carlos Rivera",
        voterNumber: "VN-2023-001234",
        precinct: "001A",
        barangay: "San Antonio"
      }
    };
    
    return baseData[type as keyof typeof baseData] || {};
  };

  const getMockIssues = (type: string): string[] => {
    const possibleIssues = [
      "Image quality could be improved",
      "Some text appears slightly blurred",
      "Document edges not fully visible",
      "Lighting conditions suboptimal"
    ];
    
    return Math.random() > 0.5 ? [] : [possibleIssues[Math.floor(Math.random() * possibleIssues.length)]];
  };

  const formatDocumentType = (type: string): string => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="document-verification-demo">
      <div className="verification-header">
        <h2>{formatDocumentType(documentType)} Verification</h2>
        <p>AI-powered document authentication and data extraction</p>
      </div>

      {imageData && (
        <div className="document-preview">
          <img src={imageData} alt="Document to verify" />
        </div>
      )}

      <div className="verification-controls">
        <button 
          onClick={simulateVerification} 
          disabled={isVerifying}
          className="verify-button"
        >
          {isVerifying ? '🔄 Verifying...' : '🔍 Start Verification'}
        </button>
      </div>

      {isVerifying && (
        <div className="verification-progress">
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
          <p>Analyzing document structure and authenticity...</p>
        </div>
      )}

      {verificationResult && (
        <div className="verification-results">
          <div className={`result-status ${verificationResult.isValid ? 'valid' : 'invalid'}`}>
            <span className="status-icon">
              {verificationResult.isValid ? '✅' : '❌'}
            </span>
            <span className="status-text">
              {verificationResult.isValid ? 'Document Verified' : 'Verification Failed'}
            </span>
            <span className="confidence">
              Confidence: {verificationResult.confidence}%
            </span>
          </div>

          <div className="extracted-data">
            <h3>Extracted Information</h3>
            <div className="data-grid">
              {Object.entries(verificationResult.extractedData).map(([key, value]) => (
                <div key={key} className="data-item">
                  <label>{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:</label>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          </div>

          {verificationResult.issues.length > 0 && (
            <div className="verification-issues">
              <h3>Issues Detected</h3>
              <ul>
                {verificationResult.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentVerificationDemo;