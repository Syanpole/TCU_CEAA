import React, { useState, useEffect } from 'react';
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';
import { Amplify } from 'aws-amplify';
import { apiClient } from '../services/authService';
import '@aws-amplify/ui-react/styles.css';
import './BiometricLivenessCapture.css';

// Configure Amplify (minimal config - we're using custom backend)
// Note: We're using our own apiClient, so Amplify config is minimal
try {
  Amplify.configure({});
} catch (error) {
  console.warn('Amplify configuration skipped:', error);
}

interface BiometricLivenessCaptureProps {
  onComplete: (result: LivenessResult) => void;
  onError: (error: string) => void;
  studentId?: string;
}

export interface LivenessResult {
  sessionId: string;
  confidenceScore: number;
  isLive: boolean;
  auditImageUrl?: string;
  referenceImageUrl?: string;
  verificationTimestamp: string;
}

export const BiometricLivenessCapture: React.FC<BiometricLivenessCaptureProps> = ({
  onComplete,
  onError,
  studentId
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [attemptCount, setAttemptCount] = useState(0);
  const [deviceFingerprint, setDeviceFingerprint] = useState<string>('');
  const [isInitialized, setIsInitialized] = useState(false);

  // Generate device fingerprint on mount
  useEffect(() => {
    generateDeviceFingerprint().then(() => {
      setIsInitialized(true);
    });
  }, []);

  const generateDeviceFingerprint = async (): Promise<void> => {
    try {
      // Create a unique device fingerprint using available browser data
      const components = [
        navigator.userAgent,
        navigator.language,
        new Date().getTimezoneOffset(),
        window.screen.width + 'x' + window.screen.height,
        window.screen.colorDepth,
        navigator.hardwareConcurrency || 0,
        (navigator as any).deviceMemory || 0,
      ];

      // Add canvas fingerprint
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('Browser fingerprint', 2, 2);
        components.push(canvas.toDataURL());
      }

      // Hash the components
      const fingerprint = await hashString(components.join('|||'));
      setDeviceFingerprint(fingerprint);
    } catch (error) {
      console.error('Failed to generate device fingerprint:', error);
    }
  };

  const hashString = async (str: string): Promise<string> => {
    const encoder = new TextEncoder();
    const data = encoder.encode(str);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  const createLivenessSession = async () => {
    setLoading(true);
    setErrorMessage('');

    try {
      // Check attempt count
      if (attemptCount >= 3) {
        setErrorMessage('Maximum verification attempts reached. Please try again later.');
        onError('Maximum verification attempts reached. Please try again later.');
        return;
      }

      // Get user's IP and location
      const ipResponse = await fetch('https://api.ipify.org?format=json');
      const ipData = await ipResponse.json();
      const userIp = ipData.ip;

      // Create session with backend
      const response = await apiClient.post<{session_id: string}>('/face-verification/create-liveness-session/', {
        student_id: studentId,
        device_fingerprint: deviceFingerprint,
        ip_address: userIp,
        attempt_number: attemptCount + 1
      });

      if (response.data.session_id) {
        console.log('✅ Session created:', response.data.session_id);
        console.log('Session response:', response.data);
        setSessionId(response.data.session_id);
        setAttemptCount(prev => prev + 1);
      } else {
        throw new Error('No session ID received from server');
      }
    } catch (error: any) {
      console.error('Failed to create liveness session:', error);
      let errorMsg = 'Failed to start face verification. Please try again.';
      
      if (error.response?.status === 429) {
        errorMsg = error.response?.data?.error || 'Too many attempts. Please wait before trying again.';
      } else if (error.response?.data?.error) {
        errorMsg = error.response.data.error;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setErrorMessage(errorMsg);
      onError(errorMsg);
      
      // Make sure sessionId is null on error
      setSessionId(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisComplete = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      // Verify the liveness check with backend
      const response = await apiClient.post<{
        session_id: string;
        confidence_score: number;
        is_live: boolean;
        audit_image_url?: string;
        reference_image_url?: string;
      }>('/face-verification/verify-liveness/', {
        session_id: sessionId,
        device_fingerprint: deviceFingerprint
      });

      const result: LivenessResult = {
        sessionId: response.data.session_id,
        confidenceScore: response.data.confidence_score,
        isLive: response.data.is_live,
        auditImageUrl: response.data.audit_image_url,
        referenceImageUrl: response.data.reference_image_url,
        verificationTimestamp: new Date().toISOString()
      };

      // Check if confidence score meets threshold
      if (result.confidenceScore < 80) {
        setErrorMessage(`Verification confidence too low (${result.confidenceScore}%). Please try again in better lighting.`);
        onError(`Low confidence score: ${result.confidenceScore}%`);
        
        // Allow retry if under max attempts
        if (attemptCount < 3) {
          setTimeout(() => {
            setSessionId(null);
            setErrorMessage('');
          }, 3000);
        }
        return;
      }

      if (!result.isLive) {
        setErrorMessage('Liveness check failed. Please ensure you are using a live camera and follow the instructions carefully.');
        onError('Liveness check failed');
        
        // Allow retry if under max attempts
        if (attemptCount < 3) {
          setTimeout(() => {
            setSessionId(null);
            setErrorMessage('');
          }, 3000);
        }
        return;
      }

      // Success!
      onComplete(result);
    } catch (error: any) {
      console.error('Liveness verification failed:', error);
      const errorMsg = error.response?.data?.error || 'Verification failed. Please try again.';
      setErrorMessage(errorMsg);
      onError(errorMsg);
      
      // Allow retry if under max attempts
      if (attemptCount < 3) {
        setTimeout(() => {
          setSessionId(null);
          setErrorMessage('');
        }, 3000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleError = (error: any) => {
    console.error('Liveness detector error:', error);
    
    // Extract detailed error information
    let errorMsg = 'An error occurred during face verification.';
    if (error?.message) {
      errorMsg = error.message;
    } else if (error?.toString) {
      errorMsg = error.toString();
    }
    
    // Check if it's an AWS configuration issue
    if (errorMsg.includes('SessionNotFoundException') || errorMsg.includes('session') || errorMsg.includes('not found')) {
      errorMsg = '⚙️ AWS Rekognition is not properly configured. The session ID from the backend is not valid in AWS. Please configure AWS credentials in the backend settings.';
    }
    
    console.error('Formatted error:', errorMsg);
    setErrorMessage(errorMsg);
    onError(errorMsg);
    
    // Reset session to allow retry
    setSessionId(null);
  };

  return (
    <div className="biometric-liveness-container">
      <div className="biometric-header">
        <h3>🔐 Face Verification</h3>
        <p>Please complete the face liveness check to verify your identity</p>
        {attemptCount > 0 && (
          <div className="attempt-counter">
            Attempt {attemptCount} of 3
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="biometric-error">
          <span className="error-icon">⚠️</span>
          <p>{errorMessage}</p>
        </div>
      )}

      {!sessionId && !loading && (
        <div className="biometric-start">
          <div className="instructions">
            <h4>Before you start:</h4>
            <ul>
              <li>✓ Find a well-lit area</li>
              <li>✓ Remove glasses and face coverings</li>
              <li>✓ Hold your device at eye level</li>
              <li>✓ Follow the on-screen instructions</li>
            </ul>
          </div>
          <button 
            className="start-verification-btn"
            onClick={createLivenessSession}
            disabled={attemptCount >= 3 || !isInitialized || loading}
          >
            {!isInitialized ? 'Initializing...' : attemptCount >= 3 ? 'Maximum Attempts Reached' : 'Start Verification'}
          </button>
        </div>
      )}

      {loading && !sessionId && (
        <div className="biometric-loading">
          <div className="spinner"></div>
          <p>Initializing secure verification session...</p>
        </div>
      )}

      {sessionId && (
        <div className="liveness-detector-wrapper">
          <FaceLivenessDetector
            sessionId={sessionId}
            region="us-east-1"
            onAnalysisComplete={handleAnalysisComplete}
            onError={handleError}
            components={{
              PhotosensitiveWarning: () => (
                <div className="custom-warning">
                  <h3>⚠️ Photosensitive Warning</h3>
                  <p>This check displays colored lights. Use caution if you are photosensitive.</p>
                </div>
              )
            }}
          />
        </div>
      )}

      {attemptCount >= 3 && (
        <div className="max-attempts-warning">
          <h4>🚫 Maximum Attempts Reached</h4>
          <p>
            You have reached the maximum number of verification attempts. 
            Please contact support for assistance or try again in 24 hours.
          </p>
        </div>
      )}
    </div>
  );
};

export default BiometricLivenessCapture;
