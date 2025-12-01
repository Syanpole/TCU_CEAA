import React, { useState, useEffect } from 'react';
import './SubmissionCountdownTimer.css';

interface SubmissionCountdownTimerProps {
  expiresAt: string; // ISO string
  onExpire?: () => void;
}

const SubmissionCountdownTimer: React.FC<SubmissionCountdownTimerProps> = ({
  expiresAt,
  onExpire,
}) => {
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [hasExpired, setHasExpired] = useState(false);

  useEffect(() => {
    const calculateTimeRemaining = () => {
      const now = new Date().getTime();
      const expiry = new Date(expiresAt).getTime();
      const remaining = Math.max(0, expiry - now);
      
      setTimeRemaining(remaining);
      
      if (remaining === 0 && !hasExpired) {
        setHasExpired(true);
        if (onExpire) {
          onExpire();
        }
      }
    };

    // Calculate immediately
    calculateTimeRemaining();

    // Update every second
    const interval = setInterval(calculateTimeRemaining, 1000);

    return () => clearInterval(interval);
  }, [expiresAt, onExpire, hasExpired]);

  const formatTime = (milliseconds: number): string => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const getTimerColor = (): string => {
    const twoHoursInMs = 2 * 60 * 60 * 1000;
    const percentage = (timeRemaining / twoHoursInMs) * 100;

    if (percentage > 50) return '#4caf50'; // Green
    if (percentage > 25) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  const getTimerSeverity = (): 'success' | 'warning' | 'error' => {
    const twoHoursInMs = 2 * 60 * 60 * 1000;
    const percentage = (timeRemaining / twoHoursInMs) * 100;

    if (percentage > 50) return 'success';
    if (percentage > 25) return 'warning';
    return 'error';
  };

  const getProgressValue = (): number => {
    const twoHoursInMs = 2 * 60 * 60 * 1000;
    return (timeRemaining / twoHoursInMs) * 100;
  };

  if (hasExpired) {
    return (
      <div className="countdown-expired">
        <div className="expired-icon">⚠️</div>
        <div className="expired-content">
          <h3>Submission Time Expired</h3>
          <p>Your 2-hour submission window has expired. Please contact the administrator to reset your session.</p>
        </div>
      </div>
    );
  }

  const timerColor = getTimerColor();
  const severity = getTimerSeverity();

  return (
    <div 
      className={`countdown-timer countdown-${severity}`}
      style={{ 
        borderColor: timerColor,
        background: `linear-gradient(135deg, ${timerColor}15 0%, ${timerColor}05 100%)`
      }}
    >
      <div className="timer-header">
        <div className="timer-icon" style={{ color: timerColor }}>⏰</div>
        <div className="timer-info">
          <div className="timer-label">Time Remaining to Complete Submissions</div>
          <div className="timer-display" style={{ color: timerColor }}>
            {formatTime(timeRemaining)}
          </div>
        </div>
      </div>

      <div className="progress-bar-container">
        <div 
          className="progress-bar"
          style={{ 
            width: `${getProgressValue()}%`,
            backgroundColor: timerColor 
          }}
        />
      </div>

      <div className="timer-message">
        {severity === 'error' && (
          <span className="message-error">
            ⚠️ Hurry! Less than 30 minutes remaining
          </span>
        )}
        {severity === 'warning' && (
          <span className="message-warning">
            ⏰ Running low on time - please complete your submissions soon
          </span>
        )}
        {severity === 'success' && (
          <span className="message-success">
            Your progress is being auto-saved every 30 seconds
          </span>
        )}
      </div>
    </div>
  );
};

export default SubmissionCountdownTimer;
