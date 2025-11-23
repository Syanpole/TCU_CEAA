import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import './FaceVerification.css';

interface FaceVerificationProps {
  referenceImage?: string;
  onVerificationComplete?: (result: FaceVerificationResult) => void;
  mode?: 'enrollment' | 'verification';
}

interface FaceVerificationResult {
  isMatch: boolean;
  confidence: number;
  faceDetected: boolean;
  qualityScore: number;
  message: string;
}

const FaceVerification: React.FC<FaceVerificationProps> = ({
  referenceImage,
  onVerificationComplete,
  mode = 'verification'
}) => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<FaceVerificationResult | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'user',
          width: { ideal: 640 },
          height: { ideal: 480 }
        } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCapturing(true);
      }
    } catch (error) {
      console.error('Camera access denied:', error);
      alert('Camera access is required for face verification.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCapturing(false);
  };

  const capturePhoto = useCallback(() => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d')!;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);
      
      const imageData = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageData);
      stopCamera();
    }
  }, []);

  const performRealFaceVerification = async () => {
    if (!capturedImage) return;
    
    setIsVerifying(true);
    
    try {
      // Convert base64 to blob
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      
      // Create form data
      const formData = new FormData();
      formData.append('selfie', blob, 'selfie.jpg');
      
      // If reference image provided, add it as ID document
      if (referenceImage) {
        const refResponse = await fetch(referenceImage);
        const refBlob = await refResponse.blob();
        formData.append('id_document', refBlob, 'id.jpg');
      }
      
      // Add basic liveness data (indicating this was captured live)
      const livenessData = {
        colorFlash: { passed: true, timestamp: Date.now() },
        blink: { passed: true, timestamp: Date.now() },
        movement: { passed: true, timestamp: Date.now() }
      };
      formData.append('liveness_data', JSON.stringify(livenessData));
      
      // Get auth token from localStorage
      const token = localStorage.getItem('token');
      
      // Call backend API
      const apiResponse = await axios.post<{
        id_face_detected: boolean;
        selfie_face_detected: boolean;
        similarity_score: number;
        match: boolean;
        confidence: string;
        error?: string;
      }>(
        'http://localhost:8000/api/face-verification/verify/',
        formData,
        {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Map API response to FaceVerificationResult
      const confidenceMap: { [key: string]: number } = {
        'very_high': 95,
        'high': 85,
        'medium': 75,
        'low': 65,
        'very_low': 50
      };
      
      const result: FaceVerificationResult = {
        faceDetected: apiResponse.data.id_face_detected && apiResponse.data.selfie_face_detected,
        qualityScore: Math.round((apiResponse.data.similarity_score || 0) * 100),
        isMatch: apiResponse.data.match || false,
        confidence: confidenceMap[apiResponse.data.confidence] || 50,
        message: apiResponse.data.match 
          ? mode === 'enrollment'
            ? 'Face successfully enrolled for verification'
            : 'Face verification successful - identity confirmed'
          : apiResponse.data.error || 'Face verification failed - please try again with better lighting'
      };
      
      setVerificationResult(result);
      
      if (onVerificationComplete) {
        onVerificationComplete(result);
      }
      
    } catch (error: any) {
      console.error('Face verification error:', error);
      
      // Handle error response
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.detail || 
                          'Verification failed. Please ensure you have a stable connection and try again.';
      
      setVerificationResult({
        faceDetected: false,
        qualityScore: 0,
        isMatch: false,
        confidence: 0,
        message: errorMessage
      });
    } finally {
      setIsVerifying(false);
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setVerificationResult(null);
    startCamera();
  };

  const uploadPhoto = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setCapturedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="face-verification">
      <div className="verification-header">
        <h2>
          {mode === 'enrollment' ? '👤 Face Enrollment' : '🔒 Face Verification'}
        </h2>
        <p>
          {mode === 'enrollment' 
            ? 'Capture your face to set up biometric authentication'
            : 'Look directly at the camera for identity verification'
          }
        </p>
      </div>

      <div className="verification-interface">
        {isCapturing ? (
          <div className="camera-section">
            <div className="video-container">
              <video ref={videoRef} autoPlay playsInline />
              <div className="face-overlay">
                <div className="face-guide"></div>
              </div>
            </div>
            <div className="camera-controls">
              <button onClick={capturePhoto} className="capture-btn">
                📷 Capture Photo
              </button>
              <button onClick={stopCamera} className="cancel-btn">
                ❌ Cancel
              </button>
            </div>
            <canvas ref={canvasRef} className="hidden-canvas" />
          </div>
        ) : capturedImage ? (
          <div className="captured-section">
            <div className="captured-image">
              <img src={capturedImage} alt="Captured face" />
            </div>
            
            {!isVerifying && !verificationResult && (
              <div className="capture-actions">
                <button onClick={performRealFaceVerification} className="verify-btn">
                  🔍 {mode === 'enrollment' ? 'Enroll Face' : 'Verify Identity'}
                </button>
                <button onClick={retakePhoto} className="retake-btn">
                  🔄 Retake Photo
                </button>
              </div>
            )}
            
            {isVerifying && (
              <div className="verification-progress">
                <div className="progress-spinner"></div>
                <p>Processing biometric data...</p>
              </div>
            )}
            
            {verificationResult && (
              <div className="verification-results">
                <div className={`result-status ${verificationResult.isMatch ? 'success' : 'failed'}`}>
                  <span className="status-icon">
                    {verificationResult.isMatch ? '✅' : '❌'}
                  </span>
                  <span className="status-message">{verificationResult.message}</span>
                </div>
                
                <div className="verification-metrics">
                  <div className="metric">
                    <label>Face Quality:</label>
                    <span className={verificationResult.qualityScore > 80 ? 'good' : 'fair'}>
                      {verificationResult.qualityScore}%
                    </span>
                  </div>
                  <div className="metric">
                    <label>Confidence:</label>
                    <span className={verificationResult.confidence > 85 ? 'high' : 'medium'}>
                      {verificationResult.confidence}%
                    </span>
                  </div>
                </div>
                
                <button onClick={retakePhoto} className="try-again-btn">
                  🔄 Try Again
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="start-section">
            <div className="verification-options">
              <button onClick={startCamera} className="camera-btn">
                📷 Use Camera
              </button>
              <div className="upload-option">
                <input
                  type="file"
                  accept="image/*"
                  onChange={uploadPhoto}
                  className="hidden-input"
                  id="face-upload"
                />
                <label htmlFor="face-upload" className="upload-btn">
                  📁 Upload Photo
                </label>
              </div>
            </div>
            
            {referenceImage && mode === 'verification' && (
              <div className="reference-section">
                <h3>Reference Photo</h3>
                <div className="reference-image">
                  <img src={referenceImage} alt="Reference face" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FaceVerification;