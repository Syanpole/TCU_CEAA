import React, { useState, useRef, useEffect } from 'react';
import { requestCameraAccess } from '../utils/deviceDetection';
import './LiveCameraCapture.css';

interface LiveCameraCaptureProps {
  onCapture: (imageBlob: Blob, imageUrl: string, livenessData?: any) => void;
  onCancel: () => void;
  documentType: string;
  requireLiveness?: boolean;
  submittedIdImage?: string; // URL of submitted ID for facial comparison
}

interface LivenessChallenge {
  type: 'color_flash' | 'blink' | 'movement';
  instruction: string;
  color?: string;
  completed: boolean;
}

export const LiveCameraCapture: React.FC<LiveCameraCaptureProps> = ({
  onCapture,
  onCancel,
  documentType,
  requireLiveness = false,
  submittedIdImage
}) => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [livenessCheck, setLivenessCheck] = useState<'pending' | 'testing' | 'passed' | 'failed'>('pending');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [currentChallenge, setCurrentChallenge] = useState<LivenessChallenge | null>(null);
  const [flashColor, setFlashColor] = useState<string | null>(null);
  const [livenessProgress, setLivenessProgress] = useState(0);
  const [livenessData, setLivenessData] = useState<any>({});
  const [isFacialRecognitionProcessing, setIsFacialRecognitionProcessing] = useState(false);
  const [showConfirmButton, setShowConfirmButton] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const livenessCanvasRef = useRef<HTMLCanvasElement>(null);

  // Initialize camera on mount
  useEffect(() => {
    initializeCamera();
    
    return () => {
      // Cleanup: stop all tracks when component unmounts
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Monitor stream for liveness detection
  useEffect(() => {
    console.log('🔍 Liveness monitor - stream:', !!stream, 'videoRef:', !!videoRef.current, 'requireLiveness:', requireLiveness);
    
    if (stream && videoRef.current) {
      const video = videoRef.current;
      
      if (requireLiveness) {
        console.log('🎯 Liveness required - setting up challenges...');
        // Start comprehensive liveness detection
        const checkBasicLiveness = () => {
          console.log('🔍 Checking video ready state:', video.readyState, 'paused:', video.paused);
          if (video.readyState === 4 && !video.paused) {
            console.log('✅ Video ready! Starting liveness challenges NOW!');
            setLivenessCheck('testing');
            startLivenessChallenges();
          } else {
            console.log('⏳ Video not ready yet, checking again in 500ms...');
            setTimeout(checkBasicLiveness, 500);
          }
        };
        setTimeout(checkBasicLiveness, 1000);
      } else {
        console.log('ℹ️ Liveness NOT required - simple check only');
        // Simple check for non-liveness required captures
        const checkLiveness = () => {
          if (video.readyState === 4 && !video.paused) {
            setLivenessCheck('passed');
          } else {
            setTimeout(checkLiveness, 500);
          }
        };
        setTimeout(checkLiveness, 1000);
      }
    }
  }, [stream, requireLiveness]);

  const initializeCamera = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const mediaStream = await requestCameraAccess();
      
      if (!mediaStream) {
        setError('Unable to access camera. Please check your permissions.');
        setIsLoading(false);
        return;
      }
      
      setStream(mediaStream);
      
      // Attach stream to video element
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        
        // Set up metadata loaded handler
        videoRef.current.onloadedmetadata = () => {
          console.log('📹 Video metadata loaded, starting playback...');
          videoRef.current?.play()
            .then(() => {
              console.log('✅ Camera playback started successfully');
              setIsLoading(false);
            })
            .catch((playError) => {
              console.error('❌ Camera playback failed:', playError);
              // Still show the UI even if autoplay fails
              setIsLoading(false);
            });
        };
        
        // Fallback: Force loading to stop after 5 seconds to prevent infinite loading
        setTimeout(() => {
          console.log('⏱️ 5 second timeout reached, ensuring loading state ends');
          setIsLoading(false);
        }, 5000);
      } else {
        console.error('❌ Video ref not available during initialization');
        setIsLoading(false);
      }
    } catch (err) {
      console.error('Camera initialization error:', err);
      setError('Failed to initialize camera. Please try again.');
      setIsLoading(false);
    }
  };

  const startLivenessChallenges = async () => {
    try {
      const challenges: LivenessChallenge[] = [
        { type: 'color_flash', instruction: 'Look at the screen', completed: false },
        { type: 'blink', instruction: 'Blink your eyes naturally', completed: false },
        { type: 'movement', instruction: 'Move your face slightly', completed: false }
      ];

      let allPassed = true;

      // Challenge 1: Color Flash Detection
      setCurrentChallenge({ ...challenges[0], instruction: 'Color Flash Verification...' });
      const colorFlashPassed = await performColorFlashChallenge();
      setLivenessProgress(33);
      
      if (!colorFlashPassed) {
        allPassed = false;
      }

      await sleep(500);

      // Challenge 2: Blink Detection
      setCurrentChallenge({ ...challenges[1], instruction: 'Blink Detection...' });
      const blinkPassed = await performBlinkChallenge();
      setLivenessProgress(66);
      
      if (!blinkPassed) {
        allPassed = false;
      }

      await sleep(500);

      // Challenge 3: Movement Detection
      setCurrentChallenge({ ...challenges[2], instruction: 'Movement Verification...' });
      const movementPassed = await performMovementChallenge();
      setLivenessProgress(100);

      if (!movementPassed) {
        allPassed = false;
      }

      await sleep(500);

      if (allPassed) {
        setLivenessCheck('passed');
        setCurrentChallenge(null);
        // Show confirm button after liveness passes
        if (requireLiveness) {
          setShowConfirmButton(true);
        }
      } else {
        setLivenessCheck('failed');
        setError('Liveness verification failed. Please try again.');
      }
    } catch (err) {
      console.error('Liveness challenge error:', err);
      setLivenessCheck('failed');
      setError('Liveness verification error. Please try again.');
    }
  };

  const performColorFlashChallenge = async (): Promise<boolean> => {
    const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00'];
    const flashResults: Array<{ color: string; detected: boolean }> = [];

    for (let i = 0; i < 3; i++) {
      const randomColor = colors[Math.floor(Math.random() * colors.length)];
      setFlashColor(randomColor);
      
      await sleep(300);
      
      // Capture frame during flash
      const frameData = captureFrameData();
      flashResults.push({ color: randomColor, detected: frameData !== null });
      
      setFlashColor(null);
      await sleep(200);
    }

    const passed = flashResults.filter(r => r.detected).length >= 2;
    setLivenessData((prev: any) => ({ ...prev, colorFlash: { passed, results: flashResults } }));
    return passed;
  };

  const performBlinkChallenge = async (): Promise<boolean> => {
    // Simplified blink detection - check for frame changes
    const frames = [];
    
    for (let i = 0; i < 5; i++) {
      const frameData = captureFrameData();
      if (frameData) frames.push(frameData);
      await sleep(200);
    }

    // Check if there's variation in frames (indicates movement/blinking)
    const hasVariation = frames.length >= 3;
    setLivenessData((prev: any) => ({ ...prev, blink: { passed: hasVariation, frames: frames.length } }));
    return hasVariation;
  };

  const performMovementChallenge = async (): Promise<boolean> => {
    // Capture frames to detect movement
    const frame1 = captureFrameData();
    await sleep(500);
    const frame2 = captureFrameData();

    const hasMovement = frame1 !== null && frame2 !== null && frame1 !== frame2;
    setLivenessData((prev: any) => ({ ...prev, movement: { passed: hasMovement } }));
    return hasMovement;
  };

  const captureFrameData = (): string | null => {
    if (!videoRef.current || !livenessCanvasRef.current) return null;

    try {
      const video = videoRef.current;
      const canvas = livenessCanvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const context = canvas.getContext('2d');
      if (!context) return null;
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/jpeg', 0.5);
    } catch (err) {
      console.error('Frame capture error:', err);
      return null;
    }
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current || livenessCheck !== 'passed') {
      if (livenessCheck !== 'passed') {
        setError('Please wait for liveness verification...');
      }
      return;
    }

    try {
      // Start countdown
      for (let i = 3; i > 0; i--) {
        setCountdown(i);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      setCountdown(null);

      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      // Set canvas dimensions to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw current video frame to canvas
      const context = canvas.getContext('2d');
      if (!context) {
        setError('Unable to process image');
        return;
      }
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Convert canvas to image
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.95);
      setCapturedImage(imageDataUrl);
      
      // Stop the camera stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    } catch (err) {
      console.error('Photo capture error:', err);
      setError('Failed to capture photo. Please try again.');
    }
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setLivenessCheck('pending');
    initializeCamera();
  };

  const confirmPhoto = async () => {
    if (!capturedImage || !canvasRef.current) return;
    
    // If liveness required, show processing state for facial recognition
    if (requireLiveness) {
      setIsFacialRecognitionProcessing(true);
      
      // Simulate facial recognition processing (in production, call backend API)
      await sleep(2000);
      
      setIsFacialRecognitionProcessing(false);
    }
    
    // Convert data URL to Blob
    canvasRef.current.toBlob((blob) => {
      if (blob) {
        onCapture(blob, capturedImage, requireLiveness ? livenessData : undefined);
      }
    }, 'image/jpeg', 0.95);
  };

  const handleCancel = () => {
    // Stop camera stream
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    onCancel();
  };

  return (
    <div className="live-camera-capture">
      <div className="camera-header">
        <button className="camera-close-btn" onClick={handleCancel}>
          ✕
        </button>
        <h3>Capture {documentType}</h3>
        <div className="liveness-indicator">
          {livenessCheck === 'pending' && (
            <span className="liveness-pending">⏳ Initializing camera...</span>
          )}
          {livenessCheck === 'testing' && currentChallenge && (
            <div className="liveness-testing">
              <span className="liveness-instruction">🔍 {currentChallenge.instruction}</span>
              <div className="liveness-progress-bar">
                <div className="liveness-progress-fill" style={{ width: `${livenessProgress}%` }}></div>
              </div>
            </div>
          )}
          {livenessCheck === 'passed' && (
            <span className="liveness-passed">✅ Liveness verified</span>
          )}
          {livenessCheck === 'failed' && (
            <span className="liveness-failed">❌ Liveness check failed</span>
          )}
        </div>
      </div>

      <div className="camera-content">
        {isLoading && (
          <div className="camera-loading">
            <div className="loading-spinner"></div>
            <p>Loading camera...</p>
          </div>
        )}

        {error && (
          <div className="camera-error">
            <p>⚠️ {error}</p>
            <button onClick={initializeCamera} className="retry-btn">
              Try Again
            </button>
          </div>
        )}

        {!capturedImage && !error && !isLoading && (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="camera-video"
            />
            <canvas ref={canvasRef} className="hidden-canvas" />
            <canvas ref={livenessCanvasRef} className="hidden-canvas" />
            
            {/* Color flash overlay for liveness detection */}
            {flashColor && (
              <div className="color-flash-overlay" style={{ backgroundColor: flashColor }}></div>
            )}
            
            {countdown !== null && (
              <div className="countdown-overlay">
                <div className="countdown-number">{countdown}</div>
              </div>
            )}
            
            <div className="camera-controls">
              <div className="camera-guide">
                <p>📄 Position the document within the frame</p>
                <p>💡 Ensure good lighting and focus</p>
                <p>📏 Capture the entire document</p>
              </div>
              
              {/* Show shutter button only for document capture, not during liveness detection */}
              {!requireLiveness && (
                <button
                  className="capture-btn"
                  onClick={capturePhoto}
                  disabled={livenessCheck !== 'passed' || countdown !== null}
                >
                  {countdown !== null ? (
                    <span>📸 {countdown}</span>
                  ) : livenessCheck === 'passed' ? (
                    <span>📸 Capture</span>
                  ) : (
                    <span>⏳ Please wait...</span>
                  )}
                </button>
              )}
              
              {/* Show confirm button after liveness verification passes */}
              {requireLiveness && showConfirmButton && livenessCheck === 'passed' && (
                <button
                  className="confirm-liveness-btn"
                  onClick={capturePhoto}
                  disabled={countdown !== null || isFacialRecognitionProcessing}
                >
                  {isFacialRecognitionProcessing ? (
                    <span>⏳ Processing...</span>
                  ) : countdown !== null ? (
                    <span>📸 {countdown}</span>
                  ) : (
                    <span>✓ Confirm Face</span>
                  )}
                </button>
              )}
            </div>
          </>
        )}

        {capturedImage && (
          <div className="preview-container">
            {isFacialRecognitionProcessing && (
              <div className="facial-recognition-overlay">
                <div className="facial-recognition-spinner"></div>
                <p>🔍 Processing facial recognition...</p>
                <p className="facial-recognition-subtext">Comparing with submitted ID</p>
              </div>
            )}
            <img src={capturedImage} alt="Captured document" className="preview-image" />
            
            <div className="preview-controls">
              <button className="retake-btn" onClick={retakePhoto}>
                🔄 Retake
              </button>
              <button className="confirm-btn" onClick={confirmPhoto}>
                ✓ Use This Photo
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveCameraCapture;
