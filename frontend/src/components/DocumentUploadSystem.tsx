import React, { useState, useCallback } from 'react';
import './DocumentUploadSystem.css';

interface DocumentUploadSystemProps {
  onUpload: (files: File[]) => void;
  acceptedTypes?: string[];
  maxFiles?: number;
  maxFileSize?: number; // in MB
}

interface FileWithVerification {
  file: File;
  verificationStatus?: 'pending' | 'approved' | 'rejected' | 'error';
  verificationMessage?: string;
  aiConfidence?: number;
  fraudRisk?: 'low' | 'medium' | 'high';
}

const DocumentUploadSystem: React.FC<DocumentUploadSystemProps> = ({
  onUpload,
  acceptedTypes = ['image/*', '.pdf'],
  maxFiles = 5,
  maxFileSize = 10
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileWithVerification[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [verifyingFiles, setVerifyingFiles] = useState<Set<string>>(new Set());

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File ${file.name} is too large. Maximum size is ${maxFileSize}MB.`;
    }
    return null;
  };

  const performPreliminaryAIVerification = async (file: File): Promise<{
    status: 'approved' | 'rejected' | 'error';
    message: string;
    confidence: number;
    fraudRisk: 'low' | 'medium' | 'high';
  }> => {
    // Simulate AI verification (in real implementation, this would call your backend API)
    return new Promise((resolve) => {
      setTimeout(() => {
        // Basic filename analysis
        const filename = file.name.toLowerCase();
        const suspiciousPatterns = ['fake', 'test', 'sample', 'copy', 'scan', 'photo', 'pic', 'img'];
        const hasSuspiciousName = suspiciousPatterns.some(pattern => filename.includes(pattern));
        
        // Check for obvious filename mismatches (this would be more sophisticated in backend)
        const documentTypeKeywords = {
          'birth': ['birth', 'certificate', 'civil', 'psa'],
          'school': ['school', 'id', 'student', 'tcu'],
          'grade': ['grade', 'report', 'transcript', 'gwa'],
          'enrollment': ['enrollment', 'coe', 'enrolled'],
          'barangay': ['barangay', 'clearance'],
          'voter': ['voter', 'comelec', 'voting']
        };
        
        let filenameSuggestsType = 'unknown';
        let keywordMatches = 0;
        
        for (const [type, keywords] of Object.entries(documentTypeKeywords)) {
          const matches = keywords.filter(kw => filename.includes(kw)).length;
          if (matches > keywordMatches) {
            keywordMatches = matches;
            filenameSuggestsType = type;
          }
        }
        
        // Determine verification result
        if (hasSuspiciousName) {
          resolve({
            status: 'rejected',
            message: 'Filename contains suspicious patterns that may indicate fraudulent document',
            confidence: 0.1,
            fraudRisk: 'high'
          });
        } else if (keywordMatches === 0) {
          resolve({
            status: 'approved',
            message: 'File passed preliminary AI verification',
            confidence: 0.7,
            fraudRisk: 'low'
          });
        } else {
          // In a real implementation, this would cross-reference with actual document content
          resolve({
            status: 'approved',
            message: 'File passed preliminary AI verification',
            confidence: 0.8,
            fraudRisk: 'low'
          });
        }
      }, 1500); // Simulate processing time
    });
  };

  const handleFiles = useCallback(async (files: FileList) => {
    const fileArray = Array.from(files);
    const newErrors: string[] = [];
    const validFiles: FileWithVerification[] = [];

    if (uploadedFiles.length + fileArray.length > maxFiles) {
      newErrors.push(`Maximum ${maxFiles} files allowed.`);
      return;
    }

    for (const file of fileArray) {
      const error = validateFile(file);
      if (error) {
        newErrors.push(error);
      } else {
        const fileWithVerification: FileWithVerification = {
          file: file,
          verificationStatus: 'pending'
        };
        validFiles.push(fileWithVerification);
        
        // Start AI verification
        setVerifyingFiles(prev => new Set(prev).add(file.name));
        try {
          const verification = await performPreliminaryAIVerification(file);
          fileWithVerification.verificationStatus = verification.status;
          fileWithVerification.verificationMessage = verification.message;
          fileWithVerification.aiConfidence = verification.confidence;
          fileWithVerification.fraudRisk = verification.fraudRisk;
        } catch (error) {
          fileWithVerification.verificationStatus = 'error';
          fileWithVerification.verificationMessage = 'AI verification failed';
        } finally {
          setVerifyingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(file.name);
            return newSet;
          });
        }
      }
    }

    if (newErrors.length > 0) {
      setErrors(newErrors);
    } else {
      setErrors([]);
      const updatedFiles = [...uploadedFiles, ...validFiles];
      setUploadedFiles(updatedFiles);
      // Extract just the File objects for the callback
      onUpload(updatedFiles.map(fwv => fwv.file));
    }
  }, [uploadedFiles, maxFiles, maxFileSize, onUpload]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (index: number) => {
    const updatedFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(updatedFiles);
    // Extract just the File objects for the callback
    onUpload(updatedFiles.map(fwv => fwv.file));
  };

  return (
    <div className="document-upload-system">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h3>Upload Documents</h3>
          <p>Drag and drop files here or click to browse</p>
          <input
            type="file"
            multiple
            accept={acceptedTypes.join(',')}
            onChange={handleFileInput}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label htmlFor="file-upload" className="upload-button">
            Choose Files
          </label>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="upload-errors">
          {errors.map((error, index) => (
            <div key={index} className="error-message">
              ⚠️ {error}
            </div>
          ))}
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h4>Uploaded Files ({uploadedFiles.length}/{maxFiles})</h4>
          {uploadedFiles.map((fileWithVerification, index) => {
            const file = fileWithVerification.file;
            return (
              <div key={index} className={`file-item ${fileWithVerification.verificationStatus ? `verification-${fileWithVerification.verificationStatus}` : ''}`}>
                <div className="file-info">
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                  {verifyingFiles.has(fileWithVerification.file.name) && (
                    <div className="verification-indicator verifying">
                      <div className="verification-spinner"></div>
                      <span>AI Verifying...</span>
                    </div>
                  )}
                  {fileWithVerification.verificationStatus && !verifyingFiles.has(fileWithVerification.file.name) && (
                    <div className={`verification-indicator ${fileWithVerification.verificationStatus}`}>
                      {fileWithVerification.verificationStatus === 'approved' && <span>✅ AI Approved</span>}
                      {fileWithVerification.verificationStatus === 'rejected' && <span>❌ AI Rejected</span>}
                      {fileWithVerification.verificationStatus === 'error' && <span>⚠️ Verification Error</span>}
                      {fileWithVerification.aiConfidence && (
                        <span className="confidence-score">
                          ({(fileWithVerification.aiConfidence * 100).toFixed(0)}% confidence)
                        </span>
                      )}
                      {fileWithVerification.fraudRisk === 'high' && (
                        <span className="fraud-warning">🚨 High Fraud Risk</span>
                      )}
                    </div>
                  )}
                </div>
                {fileWithVerification.verificationMessage && (
                  <div className="verification-message">
                    {fileWithVerification.verificationMessage}
                  </div>
                )}
                <button 
                  onClick={() => removeFile(index)}
                  className="remove-file"
                  disabled={verifyingFiles.has(fileWithVerification.file.name)}
                >
                  ❌
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default DocumentUploadSystem;