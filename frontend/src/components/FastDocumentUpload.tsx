import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, Clock, AlertCircle, Zap } from 'lucide-react';

// Type definitions
interface VerificationResult {
  success: boolean;
  verification_result?: {
    is_valid_document: boolean;
    confidence_score: number;
    performance_note?: string;
    analysis_summary?: string;
  };
  performance_rating?: string;
  processing_time: number;
}

interface FastDocumentUploadProps {
  onUploadComplete?: (result: VerificationResult) => void;
}

type UploadState = 'idle' | 'checking' | 'uploading' | 'processing' | 'complete' | 'error';

const FastDocumentUpload: React.FC<FastDocumentUploadProps> = ({ onUploadComplete }) => {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [progress, setProgress] = useState<number>(0);
  const [message, setMessage] = useState<string>('');
  const [processingTime, setProcessingTime] = useState<number>(0);
  const [file, setFile] = useState<File | null>(null);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Quick format check before upload
      quickFileCheck(selectedFile);
    }
  };

  const quickFileCheck = async (file: File) => {
    setUploadState('checking');
    setMessage('Checking file format...');
    setProgress(10);

    const formData = new FormData();
    formData.append('document', file);

    try {
      const response = await fetch('/api/ai-verification/quick-check/', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.valid_format) {
        setMessage('✅ File format looks good!');
        setProgress(20);
        setTimeout(() => startFullVerification(), 500);
      } else {
        setUploadState('error');
        setMessage(`❌ ${result.message}`);
      }
    } catch (error) {
      setUploadState('error');
      setMessage('Failed to check file format');
    }
  };

  const startFullVerification = async () => {
    if (!file) return;
    
    setUploadState('processing');
    setMessage('🤖 AI is analyzing your document...');
    setProgress(30);

    const startTime = Date.now();

    // Simulate progress updates for better UX
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev < 80) return prev + 10;
        return prev;
      });
    }, 200);

    try {
      // Upload and verify document
      const formData = new FormData();
      formData.append('document', file);
      formData.append('document_type', 'birth_certificate'); // This should come from user selection

      const response = await fetch('/api/ai-verification/fast-verify/', {
        method: 'POST',
        body: formData,
      });

      const result: VerificationResult = await response.json();
      const endTime = Date.now();
      const totalTime = (endTime - startTime) / 1000;

      clearInterval(progressInterval);
      setProcessingTime(totalTime);
      setProgress(100);
      setVerificationResult(result);

      if (result.success && result.verification_result?.is_valid_document) {
        setUploadState('complete');
        setMessage(`🎉 Document verified in ${totalTime.toFixed(1)}s!`);
        if (onUploadComplete) onUploadComplete(result);
      } else {
        setUploadState('error');
        setMessage(`❌ Document verification failed: ${result.verification_result?.analysis_summary || 'Unknown error'}`);
      }
    } catch (error) {
      clearInterval(progressInterval);
      setUploadState('error');
      setMessage('Verification failed. Please try again.');
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

  const getStateIcon = () => {
    switch (uploadState) {
      case 'checking':
      case 'processing':
        return <Clock className="animate-spin" size={24} />;
      case 'complete':
        return <CheckCircle className="text-green-500" size={24} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={24} />;
      default:
        return <Upload size={24} />;
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
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      fileInput?.click();
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
          <Zap className="text-yellow-500" size={20} />
          Lightning Fast AI Verification
        </h3>
        <p className="text-sm text-gray-600">
          Upload your document and get instant AI verification in seconds!
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${getStateColor()}`}
        onClick={handleUploadAreaClick}
        style={{ cursor: uploadState === 'idle' ? 'pointer' : 'default' }}
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
                <div>⚡ Processing time: {processingTime.toFixed(2)}s</div>
                <div>🤖 Confidence: {(verificationResult?.verification_result?.confidence_score ? verificationResult.verification_result.confidence_score * 100 : 0).toFixed(0)}%</div>
                {verificationResult?.verification_result?.performance_note && (
                  <div className="text-blue-600 font-medium">
                    {verificationResult.verification_result.performance_note}
                  </div>
                )}
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
          <h4 className="font-medium mb-2">📊 Performance Details</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Processing Time:</span>
              <span className="font-medium ml-2">{processingTime.toFixed(2)}s</span>
            </div>
            <div>
              <span className="text-gray-600">Performance:</span>
              <span className="font-medium ml-2 text-green-600">
                {verificationResult?.performance_rating || 'Excellent'}
              </span>
            </div>
            <div>
              <span className="text-gray-600">AI Confidence:</span>
              <span className="font-medium ml-2">
                {(verificationResult?.verification_result?.confidence_score ? verificationResult.verification_result.confidence_score * 100 : 0).toFixed(0)}%
              </span>
            </div>
            <div>
              <span className="text-gray-600">Status:</span>
              <span className="font-medium ml-2 text-green-600">
                {verificationResult?.verification_result?.is_valid_document ? 'Approved' : 'Needs Review'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Quick Tips */}
      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="font-medium text-yellow-800 mb-1">💡 For Fastest Processing:</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Use clear, well-lit photos</li>
          <li>• Keep file size under 5MB for instant processing</li>
          <li>• Ensure all text is readable</li>
          <li>• Avoid blurry or rotated images</li>
        </ul>
      </div>
    </div>
  );
};

export default FastDocumentUpload;
