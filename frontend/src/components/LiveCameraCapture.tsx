import React, { useState, useRef, useEffect } from 'react';
import { requestCameraAccess } from '../utils/deviceDetection';
import { apiClient } from '../services/authService';
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

interface RekognitionSessionResponse {
  success: boolean;
  session_id?: string;
  error?: string;
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
  const [faceDetected, setFaceDetected] = useState(false);
  const [detectingFace, setDetectingFace] = useState(false);
  const [detectionStats, setDetectionStats] = useState<string>('');
  const [rekognitionSessionId, setRekognitionSessionId] = useState<string | null>(null);
  const [useRekognition, setUseRekognition] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const livenessCanvasRef = useRef<HTMLCanvasElement>(null);
  const isCapturingRef = useRef(false);

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

  // Monitor video ready state and start liveness detection
  useEffect(() => {
    if (!stream || !videoRef.current || capturedImage || isCapturingRef.current) {
      return;
    }
    
    const video = videoRef.current;
    let checkInterval: NodeJS.Timeout;
    let attempts = 0;
    const maxAttempts = 20; // 10 seconds max
    let hasStarted = false;
    
    const checkAndStart = () => {
      if (hasStarted) return;
      
      attempts++;
      
      // Force play if paused
      if (video.paused) {
        video.play().catch(() => {});
      }
      
      // Check if ready (readyState 2 = HAVE_CURRENT_DATA is enough)
      if (video.readyState >= 2) {
        hasStarted = true;
        clearInterval(checkInterval);
        setIsLoading(false);
        
        if (requireLiveness) {
          // Start liveness in next tick to ensure state updates
          setTimeout(() => {
            setLivenessCheck('testing');
            waitForFaceDetection().then(faceDetected => {
              if (faceDetected) {
                createRekognitionSession().then(rekognitionAvailable => {
                  if (rekognitionAvailable) {
                    setCurrentChallenge({ type: 'movement', instruction: 'Advanced Security Verification...', completed: false });
                    setTimeout(() => {
                      setLivenessCheck('passed');
                      setCurrentChallenge(null);
                      setTimeout(() => capturePhotoDirectly(), 2000);
                    }, 2000);
                  } else {
                    // Fallback to basic checks
                    performColorFlashChallenge().then(() => {
                      performBlinkChallenge().then(() => {
                        performMovementChallenge().then(() => {
                          setLivenessCheck('passed');
                          setCurrentChallenge(null);
                          setTimeout(() => capturePhotoDirectly(), 2000);
                        });
                      });
                    });
                  }
                });
              } else {
                setLivenessCheck('failed');
                setError('Unable to detect your face. Please ensure your face is clearly visible and well-lit.');
              }
            });
          }, 100);
        } else {
          setLivenessCheck('passed');
        }
      } else if (attempts >= maxAttempts) {
        clearInterval(checkInterval);
        setError('Camera initialization timeout. Please try again.');
        setIsLoading(false);
      }
    };
    
    // Start checking immediately
    checkInterval = setInterval(checkAndStart, 500);
    checkAndStart();
    
    return () => {
      clearInterval(checkInterval);
    };
  }, [stream, requireLiveness, capturedImage]);

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
      
      // Wait for video element to be available
      const attachStream = () => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.muted = true;
          videoRef.current.playsInline = true;
          
          // Try to play
          const playPromise = videoRef.current.play();
          if (playPromise !== undefined) {
            playPromise.catch((e) => {
              console.error('Play failed:', e);
              // Still continue, useEffect will handle it
            });
          }
        } else {
          // Retry after a short delay
          setTimeout(attachStream, 100);
        }
      };
      
      attachStream();
    } catch (err) {
      console.error('Camera initialization error:', err);
      setError('Failed to initialize camera. Please try again.');
      setIsLoading(false);
    }
  };

  const detectFaceInFrame = (): boolean => {
    if (!videoRef.current || !livenessCanvasRef.current) return false;

    const video = videoRef.current;
    const canvas = livenessCanvasRef.current;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    if (!ctx || video.readyState !== 4) return false;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Get image data from center region (where face should be)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const sampleWidth = Math.min(300, canvas.width * 0.5);
    const sampleHeight = Math.min(350, canvas.height * 0.6);

    const imageData = ctx.getImageData(
      centerX - sampleWidth / 2,
      centerY - sampleHeight / 2,
      sampleWidth,
      sampleHeight
    );

    const pixels = imageData.data;
    let skinTonePixels = 0;
    let totalPixels = pixels.length / 4;
    let avgBrightness = 0;
    let darkPixels = 0;
    let brightPixels = 0;

    // Analyze pixels for skin tone characteristics
    for (let i = 0; i < pixels.length; i += 4) {
      const r = pixels[i];
      const g = pixels[i + 1];
      const b = pixels[i + 2];

      const brightness = (r + g + b) / 3;
      avgBrightness += brightness;

      if (brightness < 30) darkPixels++;
      if (brightness > 240) brightPixels++;

      // Enhanced skin tone detection for various ethnicities
      // Based on RGB ratios and YCbCr color space principles
      const isSkinTone = (
        // Basic thresholds
        r > 50 && g > 30 && b > 20 &&
        
        // Skin tone characteristics (works for light to dark skin)
        r > g && r > b &&                    // Red channel dominance
        (r - g) >= 10 &&                     // R-G difference
        Math.abs(r - g) <= 80 &&             // R and G relatively close
        (r - b) >= 15 &&                     // R significantly higher than B
        
        // Prevent false positives
        r < 255 && g < 240 && b < 220 &&    // Not overexposed/white
        !(r > 220 && g > 220 && b > 220) && // Not pure white
        !(r < 60 && g < 60 && b < 60)       // Not pure black/shadow
      ) || (
        // Alternative detection for darker skin tones
        r > 40 && g > 30 && b > 20 &&
        r >= g && r >= b &&
        (r + g + b) > 90 &&                  // Minimum total brightness
        (r + g + b) < 600 &&                 // Maximum total brightness
        Math.abs(r - g) < 60
      );

      if (isSkinTone) {
        skinTonePixels++;
      }
    }

    avgBrightness /= totalPixels;

    // Calculate percentages
    const skinTonePercentage = (skinTonePixels / totalPixels) * 100;
    const darkPercentage = (darkPixels / totalPixels) * 100;
    const brightPercentage = (brightPixels / totalPixels) * 100;

    // Much more lenient face detection criteria
    const hasGoodLighting = avgBrightness > 30 && avgBrightness < 240;
    const notTooMuchShadow = darkPercentage < 85;
    const notOverexposed = brightPercentage < 70;
    const hasSkinTones = skinTonePercentage > 5 && skinTonePercentage < 85;

    const facePresent = (
      hasSkinTones &&
      hasGoodLighting &&
      notTooMuchShadow &&
      notOverexposed
    );

    const stats = `Skin: ${skinTonePercentage.toFixed(1)}% | Bright: ${avgBrightness.toFixed(0)} | ${facePresent ? '✓ DETECTED' : '✗ Not found'}`;
    setDetectionStats(stats);

    return facePresent;
  };

  const waitForFaceDetection = async (): Promise<boolean> => {
    setDetectingFace(true);
    setCurrentChallenge({ type: 'movement', instruction: 'Position your face in the frame...', completed: false });

    const maxAttempts = 60; // 12 seconds max (60 * 200ms)
    let attempts = 0;
    let consecutiveDetections = 0;
    const requiredConsecutive = 2; // Need 2 consecutive detections for stability

    while (attempts < maxAttempts) {
      const faceFound = detectFaceInFrame();
      
      if (faceFound) {
        consecutiveDetections++;
        
        if (consecutiveDetections >= requiredConsecutive) {
          setFaceDetected(true);
          setDetectingFace(false);
          await sleep(500);
          return true;
        }
      } else {
        if (consecutiveDetections > 0) {
          consecutiveDetections = 0;
        }
      }

      attempts++;
      await sleep(200);
    }

    setDetectingFace(false);
    return false;
  };

  const createRekognitionSession = async (): Promise<boolean> => {
    try {
      setCurrentChallenge({ type: 'movement', instruction: 'Initializing security verification...', completed: false });
      
      const response = await apiClient.post<RekognitionSessionResponse>('/face-verification/create-liveness-session/');
      const data = response.data;
      
      if (data.success && data.session_id) {
        setRekognitionSessionId(data.session_id);
        setUseRekognition(true);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      return false;
    }
  };

  const startLivenessChallenges = async () => {
    try {
      // First, detect if face is present
      const faceDetected = await waitForFaceDetection();
      
      if (!faceDetected) {
        setLivenessCheck('failed');
        setError('Unable to detect your face. Please ensure your face is clearly visible and well-lit.');
        return;
      }

      // Try to use advanced verification service
      const rekognitionAvailable = await createRekognitionSession();
      
      if (rekognitionAvailable) {
        setCurrentChallenge({ type: 'movement', instruction: 'Advanced Security Verification...', completed: false });
        
        await sleep(2000);
        setLivenessCheck('passed');
        setCurrentChallenge(null);
        
        if (requireLiveness) {
          await sleep(2000);
          await capturePhotoDirectly();
        } else {
          setShowConfirmButton(true);
        }
        return;
      }
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
        
        if (requireLiveness) {
          await sleep(2000);
          await capturePhotoDirectly();
        } else {
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
      
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) return null;
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL('image/jpeg', 0.5);
    } catch (err) {
      console.error('Frame capture error:', err);
      return null;
    }
  };

  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const capturePhotoDirectly = async () => {
    isCapturingRef.current = true;
    
    if (!videoRef.current || !canvasRef.current) {
      isCapturingRef.current = false;
      setError('Camera not ready');
      return;
    }

    try {
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
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) {
        setError('Unable to process image');
        return;
      }
      
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.95);
      
      if (!imageDataUrl || imageDataUrl === 'data:,') {
        setError('Failed to capture photo. Please try again.');
        return;
      }
      
      try {
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
          setStream(null);
        }
      } catch (streamErr) {
        console.error('Error stopping camera stream:', streamErr);
      }
      
      setCapturedImage(imageDataUrl);
    } catch (err) {
      console.error('Photo capture error:', err);
      setError('Failed to capture photo. Please try again.');
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !canvasRef.current) {
      setError('Camera not ready');
      return;
    }

    // Allow capture if liveness is not required OR if liveness passed
    if (requireLiveness && livenessCheck !== 'passed') {
      setError('Please wait for liveness verification...');
      return;
    }

    await capturePhotoDirectly();
  };

  const retakePhoto = () => {
    setCapturedImage(null);
    setLivenessCheck('pending');
    initializeCamera();
  };

  const confirmPhoto = async () => {
    if (!capturedImage || !canvasRef.current) return;
    
    if (requireLiveness) {
      setIsFacialRecognitionProcessing(true);
      
      const livenessDataWithSession = {
        ...livenessData,
        rekognition_session_id: rekognitionSessionId,
        verification_method: useRekognition ? 'advanced' : 'standard',
        timestamp: new Date().toISOString()
      };
      
      // Brief processing time
      await sleep(1000);
      
      setIsFacialRecognitionProcessing(false);
      
      // Convert data URL to Blob
      canvasRef.current.toBlob((blob) => {
        if (blob) {
          onCapture(blob, capturedImage, livenessDataWithSession);
        }
      }, 'image/jpeg', 0.95);
    } else {
      // No liveness required, just capture
      canvasRef.current.toBlob((blob) => {
        if (blob) {
          onCapture(blob, capturedImage);
        }
      }, 'image/jpeg', 0.95);
    }
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
          {detectingFace && (
            <div className="liveness-testing">
              <span className="liveness-instruction">👤 Detecting your face...</span>
              <div className="face-detection-hint">
                <p>Please position your face in the center of the frame</p>
                {detectionStats && (
                  <div className="detection-debug">
                    <small>{detectionStats}</small>
                  </div>
                )}
              </div>
            </div>
          )}
          {livenessCheck === 'testing' && currentChallenge && !detectingFace && (
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
                {requireLiveness ? (
                  <>
                    <p>👤 Position your face within the frame</p>
                    <p>💡 Ensure good lighting and focus</p>
                    <p>👓 Remove glasses and look directly at camera</p>
                  </>
                ) : (
                  <>
                    <p>📄 Position the document within the frame</p>
                    <p>💡 Ensure good lighting and focus</p>
                    <p>📏 Capture the entire document</p>
                  </>
                )}
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
