import React from 'react';
import './ModernLoadingSpinner.css';

interface ModernLoadingSpinnerProps {
  text?: string;
  fullScreen?: boolean;
}

const ModernLoadingSpinner: React.FC<ModernLoadingSpinnerProps> = ({ 
  text = 'Loading your dashboard...', 
  fullScreen = true 
}) => {
  return (
    <div className={`modern-loading-container ${fullScreen ? 'fullscreen' : ''}`}>
      <div className="modern-loading-content">
        <div className="modern-spinner">
          <div className="spinner-ring ring-1"></div>
          <div className="spinner-ring ring-2"></div>
          <div className="spinner-ring ring-3"></div>
          <div className="spinner-center"></div>
        </div>
        <div className="modern-loading-text">
          <h2>{text}</h2>
          <div className="loading-dots">
            <span className="dot dot-1"></span>
            <span className="dot dot-2"></span>
            <span className="dot dot-3"></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModernLoadingSpinner;
