import React, { useState } from 'react';

// Simple version without external dependencies
const FastDocumentUpload = ({ onUploadComplete }) => {
  const [uploadState, setUploadState] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [processingTime, setProcessingTime] = useState(0);
  const [file, setFile] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      quickFileCheck(selectedFile);
    }
  };

  const quickFileCheck = async (file) => {
    setUploadState('checking');
    setMessage('Checking file format...');
    setProgress(10);

    // Quick client-side validation
    const validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
      setUploadState('error');
      setMessage('Invalid file type. Please use JPG, PNG, or PDF.');
      return;
    }

    if (file.size > maxSize) {
      setUploadState('error');
      setMessage('File too large. Maximum size is 10MB.');
      return;
    }

    if (file.size < 1000) {
      setUploadState('error');
      setMessage('File too small. Minimum size is 1KB.');
      return;
    }

    setMessage('File format accepted.');
    setProgress(20);
    setTimeout(() => startFullVerification(), 500);
  };

  const startFullVerification = async () => {
    if (!file) return;
    
    setUploadState('processing');
    setMessage('Processing document...');
    setProgress(30);

    const startTime = Date.now();

    // Simulate progress updates for better UX
    const progressInterval = setInterval(() => {
      setProgress(prev => prev < 80 ? prev + 10 : prev);
    }, 200);

    try {
      // Create FormData for upload
      const formData = new FormData();
      formData.append('document', file);
      formData.append('document_type', 'birth_certificate');

      // Make API call to fast verification endpoint
      const response = await fetch('/api/documents/upload/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCsrfToken(),
        },
      });

      const result = await response.json();
      const endTime = Date.now();
      const totalTime = (endTime - startTime) / 1000;

      clearInterval(progressInterval);
      setProcessingTime(totalTime);
      setProgress(100);
      setVerificationResult(result);

      if (result.success && result.verification_result?.is_valid_document) {
        setUploadState('complete');
        setMessage(`Document uploaded successfully!`);
        if (onUploadComplete) onUploadComplete(result);
      } else {
        setUploadState('error');
        setMessage(`Upload failed: ${result.verification_result?.analysis_summary || result.message || result.error || 'Unknown error'}`);
      }
    } catch (error) {
      clearInterval(progressInterval);
      setUploadState('error');
      setMessage('Upload failed. Please try again.');
      console.error('Upload error:', error);
    }
  };

  const resetUpload = () => {
    setUploadState('idle');
    setProgress(0);
    setMessage('');
    setFile(null);
    setVerificationResult(null);
    setProcessingTime(0);
  };

  const getCsrfToken = () => {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  };

  const getStateIcon = () => {
    switch (uploadState) {
      case 'checking':
      case 'processing':
        return <div className="animate-spin text-2xl">⏳</div>;
      case 'complete':
        return <div className="text-2xl text-green-500">✅</div>;
      case 'error':
        return <div className="text-2xl text-red-500">❌</div>;
      default:
        return <div className="text-2xl">📄</div>;
    }
  };

  const getStateColor = () => {
    switch (uploadState) {
      case 'complete':
        return 'border-green-500 bg-green-50';
      case 'error':
        return 'border-red-500 bg-red-50';
      case 'processing':
      case 'checking':
        return 'border-blue-500 bg-blue-50';
      default:
        return 'border-gray-300 hover:border-blue-400';
    }
  };

  const handleUploadAreaClick = () => {
    if (uploadState === 'idle') {
      document.getElementById('file-input')?.click();
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">
          Upload Document
        </h3>
        <p className="text-sm text-gray-600">
          Select your document to upload and verify.
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 cursor-pointer ${getStateColor()}`}
        onClick={handleUploadAreaClick}
      >
        <input
          id="file-input"
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploadState !== 'idle'}
        />

        <div className="flex flex-col items-center gap-3">
          {getStateIcon()}
          
          {uploadState === 'idle' && (
            <>
              <p className="text-lg font-medium">Click to upload document</p>
              <p className="text-sm text-gray-500">
                Supports JPG, PNG, PDF • Max 10MB
              </p>
            </>
          )}

          {(uploadState === 'checking' || uploadState === 'processing') && (
            <>
              <p className="text-lg font-medium">{message}</p>
              <div className="w-full max-w-xs bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500">{progress}% complete</p>
            </>
          )}

          {uploadState === 'complete' && (
            <>
              <p className="text-lg font-medium text-green-600">{message}</p>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Processing time: {processingTime.toFixed(2)}s</div>
              </div>
              <button
                onClick={resetUpload}
                className="mt-3 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Upload Another Document
              </button>
            </>
          )}

          {uploadState === 'error' && (
            <>
              <p className="text-lg font-medium text-red-600">{message}</p>
              <button
                onClick={resetUpload}
                className="mt-3 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
              >
                Try Again
              </button>
            </>
          )}
        </div>
      </div>

      {/* Performance Stats */}
      {uploadState === 'complete' && verificationResult && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium mb-2">Upload Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Processing Time:</span>
              <span className="font-medium ml-2">{processingTime.toFixed(2)}s</span>
            </div>
            <div>
              <span className="text-gray-600">Status:</span>
              <span className="font-medium ml-2 text-green-600">
                {verificationResult.success !== false ? 'Approved' : 'Needs Review'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">File Size:</span>
              <span className="font-medium ml-2">
                {file ? (file.size / 1024 / 1024).toFixed(1) + 'MB' : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Quick Tips */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-1">Upload Guidelines:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Use clear, well-lit photos</li>
          <li>• Keep file size under 5MB</li>
          <li>• Ensure all text is readable</li>
          <li>• Avoid blurry or rotated images</li>
        </ul>
      </div>
    </div>
  );
};

export default FastDocumentUpload;
