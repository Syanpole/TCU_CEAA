import React, { useState, useEffect } from 'react';
import { FaceLivenessDetector } from '@aws-amplify/ui-react-liveness';
import { Amplify } from 'aws-amplify';
import { apiClient } from '../services/authService';
import '@aws-amplify/ui-react/styles.css';
import './BiometricLivenessCapture.css';

// Amplify configuration will be set dynamically after getting AWS config from backend
let amplifyConfigured = false;

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

  // Initialize: fetch AWS credentials and generate device fingerprint on mount
  useEffect(() => {
    const initialize = async () => {
      try {
        // Fetch AWS credentials from backend
        const awsConfigResponse = await apiClient.get<{
          enabled: boolean;
          region: string;
          credentials: {
            accessKeyId: string;
            secretAccessKey: string;
          };
          warning?: string;
        }>('/face-verification/aws-credentials/');

        if (!awsConfigResponse.data.enabled) {
          setErrorMessage('⚙️ AWS Rekognition is not enabled. Please configure AWS in backend .env file.');
          setIsInitialized(false);
          return;
        }

        // Configure Amplify with AWS credentials
        if (!amplifyConfigured) {
          console.log('🔧 Configuring AWS Amplify with region:', awsConfigResponse.data.region);
          if (awsConfigResponse.data.warning) {
            console.warn('⚠️', awsConfigResponse.data.warning);
          }
          
          Amplify.configure({
            Auth: {
              Cognito: {
                identityPoolId: 'us-east-1:dummy-pool-id', // Not used, but required by Amplify
                region: awsConfigResponse.data.region,
                credentials: {
                  accessKeyId: awsConfigResponse.data.credentials.accessKeyId,
                  secretAccessKey: awsConfigResponse.data.credentials.secretAccessKey,
                },
              }
            }
          });
          amplifyConfigured = true;
          console.log('✅ AWS Amplify configured successfully');
        }

        // Generate device fingerprint
        await generateDeviceFingerprint();
        setIsInitialized(true);
      } catch (error: any) {
        console.error('Failed to initialize biometric capture:', error);
        setErrorMessage(
          error.response?.data?.error || 
          'Failed to initialize face verification. Please check AWS configuration.'
        );
        setIsInitialized(false);
      }
    };

    initialize();
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
      // Check AWS configuration from backend
      if (!amplifyConfigured) {
        try {
          console.log('🔧 Checking AWS configuration from backend...');
          const configResponse = await apiClient.get<{
            region: string;
            enabled: boolean;
            message: string;
          }>('/face-verification/aws-config/');
          
          console.log('✅ AWS config received:', configResponse.data);
          
          if (!configResponse.data.enabled) {
            throw new Error(
              '⚙️ AWS Rekognition is not configured in the backend.\n\n' +
              'To enable face liveness detection, configure your backend/.env file:\n\n' +
              'VERIFICATION_SERVICE_ENABLED=True\n' +
              'AWS_ACCESS_KEY_ID=your-aws-access-key\n' +
              'AWS_SECRET_ACCESS_KEY=your-aws-secret-key\n' +
              'AWS_STORAGE_BUCKET_NAME=your-s3-bucket\n' +
              'VERIFICATION_SERVICE_REGION=us-east-1\n\n' +
              'Then restart the Django server.'
            );
          }
          
          // For AWS Amplify FaceLivenessDetector to work, we need proper AWS credentials
          // Since we're creating sessions server-side, Amplify still needs to be configured
          // This is a limitation of the current setup - AWS Amplify expects client-side AWS SDK access
          
          amplifyConfigured = true;
          console.log('⚠️ AWS is enabled but Amplify needs client-side credentials');
          
          throw new Error(
            '⚙️ AWS Rekognition Face Liveness requires additional configuration.\n\n' +
            'The current setup creates sessions server-side, but AWS Amplify FaceLivenessDetector ' +
            'component requires client-side AWS credentials or Cognito Identity Pool.\n\n' +
            'For thesis demo, consider:\n' +
            '1. Use server-side only verification (no live camera widget)\n' +
            '2. Set up AWS Cognito Identity Pool for unauthenticated access\n' +
            '3. Use alternative face detection library (face-api.js, MediaPipe)\n\n' +
            'Contact your supervisor for guidance on which approach fits your thesis scope.'
          );
          
        } catch (configError: any) {
          console.error('❌ AWS configuration check failed:', configError);
          setErrorMessage(configError.message || 'AWS configuration error');
          onError(configError.message || 'AWS configuration error');
          setLoading(false);
          return;
        }
      }

      // DEV MODE: Rate limiting disabled for development
      // if (attemptCount >= 3) {
      //   setErrorMessage('Maximum verification attempts reached. Please try again later.');
      //   onError('Maximum verification attempts reached. Please try again later.');
      //   return;
      // }

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
        
        // DEV MODE: Always allow retry
        setTimeout(() => {
          setSessionId(null);
          setErrorMessage('');
        }, 3000);
        return;
      }

      if (!result.isLive) {
        setErrorMessage('Liveness check failed. Please ensure you are using a live camera and follow the instructions carefully.');
        onError('Liveness check failed');
        
        // DEV MODE: Always allow retry
        setTimeout(() => {
          setSessionId(null);
          setErrorMessage('');
        }, 3000);
        return;
      }

      // Success!
      onComplete(result);
    } catch (error: any) {
      console.error('Liveness verification failed:', error);
      const errorMsg = error.response?.data?.error || 'Verification failed. Please try again.';
      setErrorMessage(errorMsg);
      onError(errorMsg);
      
      // DEV MODE: Always allow retry
      setTimeout(() => {
        setSessionId(null);
        setErrorMessage('');
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  const handleError = (error: any) => {
    console.error('Liveness detector error:', error);
    console.error('Error type:', typeof error);
    console.error('Error keys:', error ? Object.keys(error) : 'null');
    
    // Extract detailed error information
    let errorMsg = 'An error occurred during face verification.';
    
    // Try different ways to extract error message
    if (typeof error === 'string') {
      errorMsg = error;
    } else if (error?.message) {
      errorMsg = error.message;
    } else if (error?.error) {
      errorMsg = error.error;
    } else if (error?.toString && typeof error.toString === 'function') {
      const stringified = error.toString();
      if (stringified !== '[object Object]') {
        errorMsg = stringified;
      }
    }
    
    // Try to stringify the error for more details
    try {
      const jsonError = JSON.stringify(error, null, 2);
      console.error('Error JSON:', jsonError);
      
      // If we still have generic error, try to extract more details
      if (errorMsg === 'An error occurred during face verification.' && error) {
        errorMsg = `Face verification error. Check console for details. Error type: ${error.constructor?.name || typeof error}`;
      }
    } catch (e) {
      console.error('Could not stringify error:', e);
    }
    
    // Check if it's an AWS configuration issue
    const errorStr = JSON.stringify(error).toLowerCase();
    if (errorStr.includes('sessionnotfoundexception') || 
        errorStr.includes('session') && errorStr.includes('not found') ||
        errorStr.includes('invalid') && errorStr.includes('session')) {
      errorMsg = '⚙️ AWS Rekognition is not properly configured. The session ID from the backend is not valid in AWS. Please configure AWS credentials in the backend .env file:\n\nVERIFICATION_SERVICE_ENABLED=True\nAWS_ACCESS_KEY_ID=your-key\nAWS_SECRET_ACCESS_KEY=your-secret\nAWS_STORAGE_BUCKET_NAME=your-bucket';
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
            disabled={!isInitialized || loading}
          >
            {!isInitialized ? 'Initializing...' : 'Start Verification'}
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

      {/* DEV MODE: Max attempts warning disabled
      {attemptCount >= 3 && (
        <div className="max-attempts-warning">
          <h4>🚫 Maximum Attempts Reached</h4>
          <p>
            You have reached the maximum number of verification attempts. 
            Please contact support for assistance or try again in 24 hours.
          </p>
        </div>
      )}
      */}
    </div>
  );
};

export default BiometricLivenessCapture;
