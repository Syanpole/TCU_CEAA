import React from 'react';
import './NotificationModal.css';

interface NotificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  autoClose?: boolean;
  duration?: number;
}

const NotificationModal: React.FC<NotificationModalProps> = ({
  isOpen,
  onClose,
  type,
  title,
  message,
  autoClose = true,
  duration = 5000
}) => {
  React.useEffect(() => {
    if (isOpen && autoClose) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [isOpen, autoClose, duration, onClose]);

  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      case 'info': return 'ℹ️';
      default: return 'ℹ️';
    }
  };

  const getTypeClass = () => {
    switch (type) {
      case 'success': return 'notification-success';
      case 'warning': return 'notification-warning';
      case 'error': return 'notification-error';
      case 'info': return 'notification-info';
      default: return 'notification-info';
    }
  };

  return (
    <div className="notification-overlay">
      <div className={`notification-modal ${getTypeClass()}`}>
        <div className="notification-header">
          <div className="notification-icon">
            {getIcon()}
          </div>
          <h3 className="notification-title">{title}</h3>
          <button className="notification-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="notification-body">
          <p className="notification-message">{message}</p>
        </div>
        <div className="notification-actions">
          <button className="btn-primary" onClick={onClose}>
            Got it
          </button>
        </div>
        {autoClose && (
          <div className="notification-progress">
            <div className="notification-progress-bar"></div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationModal;
