import React, { useState, useCallback, useRef } from 'react';
import { 
  ScholarshipApplication, 
  DocumentSubmission,
  SubmissionStatus 
} from '../../../types/scholarshipTypes';
import { useAIVerification } from '../../../hooks/useAIVerification';
import { useScholarshipApplication } from '../../../hooks/useScholarshipApplication';
import { FILE_CONSTRAINTS, STEP_CONFIGURATIONS } from '../../../config/scholarshipConfig';
import './DocumentUploadStep.css';

interface DocumentUploadStepProps {
  application: ScholarshipApplication;
  documentType: string;
  title: string;
  description: string;
  isCamera?: boolean;
  onComplete: () => void;
}

const DocumentUploadStep: React.FC<DocumentUploadStepProps> = ({
  application,
  documentType,
  title,
  description,
  isCamera = false,
  onComplete
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  
  const { verifyDocument, isVerificationInProgress } = useAIVerification();
  const { updateDocumentSubmission, updateVerificationResult, updateStepStatus } = useScholarshipApplication();

  // Get current submission if exists
  const currentSubmission = application.submissions[documentType as keyof typeof application.submissions] as DocumentSubmission | undefined;

  const validateFile = (file: File): string | null => {
    // Check file size
    const maxSize = file.type.includes('pdf') 
      ? FILE_CONSTRAINTS.MAX_SIZE.PDF 
      : FILE_CONSTRAINTS.MAX_SIZE.IMAGE;
    
    if (file.size > maxSize) {
      return `File size must be less than ${Math.round(maxSize / 1024 / 1024)}MB`;
    }

    // Check file type
    const acceptedFormats = file.type.includes('pdf')
      ? FILE_CONSTRAINTS.ACCEPTED_FORMATS.DOCUMENT
      : FILE_CONSTRAINTS.ACCEPTED_FORMATS.IMAGE;

    if (!acceptedFormats.includes(file.type)) {
      return 'Invalid file type. Please upload accepted formats only.';
    }

    return null;
  };

  const handleFileUpload = useCallback(async (file: File) => {
    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setUploadError(validationError);
      return;
    }

    setUploadError(null);
    setUploadProgress(0);

    try {
      // Create document submission
      const submission: DocumentSubmission = {
        fileName: file.name,
        fileData: file,
        uploadedAt: new Date(),
        status: SubmissionStatus.VERIFYING
      };

      // Update application state
      updateDocumentSubmission(documentType, submission);
      
      // Start AI verification
      setUploadProgress(25);
      
      const verificationResult = await verifyDocument(submission, {
        documentType,
        expectedMetadata: {
          studentName: application.studentName,
          studentId: application.studentId
        }
      });

      setUploadProgress(100);

      // Update verification results
      updateVerificationResult(documentType, verificationResult);

      // Update submission with verification status
      const updatedSubmission = {
        ...submission,
        status: verificationResult.status === 'verified' 
          ? SubmissionStatus.VERIFIED 
          : verificationResult.status === 'flagged' 
            ? SubmissionStatus.FLAGGED 
            : SubmissionStatus.REJECTED,
        aiVerification: verificationResult
      };

      updateDocumentSubmission(documentType, updatedSubmission);

      // Mark step as completed if verified
      if (verificationResult.status === 'verified') {
        updateStepStatus(application.currentStep, 'completed');
      }

    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError('Upload failed. Please try again.');
      setUploadProgress(0);
    }
  }, [application, documentType, verifyDocument, updateDocumentSubmission, updateVerificationResult, updateStepStatus]);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleRetry = () => {
    if (currentSubmission?.fileData) {
      handleFileUpload(currentSubmission.fileData);
    }
  };

  const handleContinue = () => {
    onComplete();
  };

  const stepConfig = STEP_CONFIGURATIONS[application.currentStep];
  const isVerifying = isVerificationInProgress(`${documentType}_${Date.now()}`);
  const isCompleted = currentSubmission?.status === SubmissionStatus.VERIFIED;
  const isFlagged = currentSubmission?.status === SubmissionStatus.FLAGGED;
  const isRejected = currentSubmission?.status === SubmissionStatus.REJECTED;

  return (
    <div className="document-upload-step">
      <div className="upload-content">
        
        {/* Instructions */}
        <div className="upload-instructions">
          <h4>Instructions</h4>
          <ul>
            {stepConfig.instructions.map((instruction, index) => (
              <li key={index}>{instruction}</li>
            ))}
          </ul>
          
          {stepConfig.acceptedFormats && (
            <div className="format-info">
              <strong>Accepted formats:</strong> {stepConfig.acceptedFormats.join(', ')}
            </div>
          )}
          
          {stepConfig.maxFileSize && (
            <div className="size-info">
              <strong>Maximum file size:</strong> {Math.round(stepConfig.maxFileSize / 1024 / 1024)}MB
            </div>
          )}
        </div>

        {/* Upload Area */}
        {!currentSubmission || isRejected ? (
          <div 
            className={`upload-area ${dragOver ? 'drag-over' : ''} ${isCamera ? 'camera-mode' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={stepConfig.acceptedFormats?.join(',')}
              onChange={handleFileSelect}
              className="file-input-hidden"
              id="document-upload-input"
              aria-label={`Upload ${stepConfig.title} document`}
              title={`Upload your ${stepConfig.title}`}
            />
            
            <div className="upload-icon">
              {isCamera ? (
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" />
                  <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM11.999 7.5a4.5 4.5 0 100 9 4.5 4.5 0 000-9z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
              )}
            </div>
            
            <div className="upload-text">
              <h4>{isCamera ? 'Take Photo' : 'Upload Document'}</h4>
              <p>
                {isCamera 
                  ? 'Click to open camera and take a photo'
                  : dragOver 
                    ? 'Drop your file here'
                    : 'Drag and drop your file here, or click to browse'
                }
              </p>
            </div>
          </div>
        ) : (
          /* Document Status Display */
          <div className="document-status">
            <div className={`status-card ${currentSubmission.status}`}>
              <div className="status-header">
                <div className="file-info">
                  <div className="file-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                    </svg>
                  </div>
                  <div className="file-details">
                    <h4>{currentSubmission.fileName}</h4>
                    <p>Uploaded {currentSubmission.uploadedAt.toLocaleDateString()}</p>
                  </div>
                </div>
                
                <div className="status-badge">
                  {currentSubmission.status === SubmissionStatus.VERIFYING && (
                    <>
                      <div className="status-spinner"></div>
                      Verifying...
                    </>
                  )}
                  {currentSubmission.status === SubmissionStatus.VERIFIED && (
                    <>
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Verified
                    </>
                  )}
                  {currentSubmission.status === SubmissionStatus.FLAGGED && (
                    <>
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                      </svg>
                      Flagged for Review
                    </>
                  )}
                  {currentSubmission.status === SubmissionStatus.REJECTED && (
                    <>
                      <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Rejected
                    </>
                  )}
                </div>
              </div>

              {/* Verification Results */}
              {currentSubmission.aiVerification && (
                <div className="verification-results">
                  <div className="confidence-score">
                    <span>AI Confidence:</span>
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill"
                        data-confidence={currentSubmission.aiVerification.confidence}
                      ></div>
                    </div>
                    <span>{currentSubmission.aiVerification.confidence}%</span>
                  </div>
                  
                  <div className="verification-feedback">
                    <p>{currentSubmission.aiVerification.feedback}</p>
                  </div>

                  {currentSubmission.aiVerification.flaggedReasons.length > 0 && (
                    <div className="flagged-reasons">
                      <h5>Issues Found:</h5>
                      <ul>
                        {currentSubmission.aiVerification.flaggedReasons.map((reason, index) => (
                          <li key={index}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="status-actions">
                {isRejected && (
                  <button className="retry-btn" onClick={handleRetry}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
                    </svg>
                    Upload New Document
                  </button>
                )}
                
                {isFlagged && (
                  <div className="flagged-notice">
                    <p>Your document has been flagged for manual review by an administrator. This may take 1-2 business days.</p>
                  </div>
                )}
                
                {isCompleted && (
                  <button className="continue-btn" onClick={handleContinue}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M9 5l7 7-7 7" />
                    </svg>
                    Continue to Next Step
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="upload-progress">
            <div className="progress-info">
              <span>Uploading and verifying document...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                data-progress={uploadProgress}
              ></div>
            </div>
          </div>
        )}

        {/* Upload Error */}
        {uploadError && (
          <div className="upload-error">
            <div className="error-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p>{uploadError}</p>
            <button onClick={() => setUploadError(null)}>Dismiss</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUploadStep;