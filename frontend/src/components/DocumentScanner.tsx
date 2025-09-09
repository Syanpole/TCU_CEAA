import React, { useState, useRef } from 'react';
import './DocumentScanner.css';

interface DocumentScannerProps {
  documentType: string;
  onCapture: (imageData: string) => void;
  onFileSelect: (file: File) => void;
}

const DocumentScanner: React.FC<DocumentScannerProps> = ({ 
  documentType, 
  onCapture, 
  onFileSelect 
}) => {
  const [isScanning, setIsScanning] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsScanning(true);
      }
    } catch (error) {
      console.error('Camera access denied:', error);
    }
  };

  const captureImage = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      context.drawImage(videoRef.current, 0, 0);
      const imageData = canvas.toDataURL('image/jpeg');
      onCapture(imageData);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="document-scanner">
      <div className="scanner-header">
        <h3>Scan {documentType}</h3>
        <p>Position your {documentType.toLowerCase()} clearly in the frame. Ensure all text is readable.</p>
      </div>

      <div className="scanner-interface">
        {isScanning ? (
          <div className="camera-view">
            <video ref={videoRef} autoPlay playsInline />
            <button onClick={captureImage} className="capture-btn">
              📷 Capture
            </button>
          </div>
        ) : (
          <div className="scanner-options">
            <button onClick={startCamera} className="use-camera-btn">
              📷 Use Camera
            </button>
            <div className="file-upload">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="upload-btn"
              >
                📁 Upload from Device
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentScanner;
