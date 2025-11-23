import React from 'react';
import './NotificationDialog.css';

interface NotificationDialogProps {
  isOpen: boolean;
  title?: string;
  message: string;
  type?: 'info' | 'warning' | 'error' | 'success';
  onConfirm?: () => void;
  onCancel?: () => void;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
}

const NotificationDialog: React.FC<NotificationDialogProps> = ({
  isOpen,
  title,
  message,
  type = 'info',
  onConfirm,
  onCancel,
  confirmText = 'OK',
  cancelText = 'Cancel',
  showCancel = true
}) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'warning':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor" className="dialog-icon warning">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
          </svg>
        );
      case 'error':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor" className="dialog-icon error">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
        );
      case 'success':
        return (
          <svg viewBox="0 0 24 24" fill="currentColor" className="dialog-icon success">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
          </svg>
        );
      default:
        return (
          <svg viewBox="0 0 24 24" fill="currentColor" className="dialog-icon info">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" />
          </svg>
        );
    }
  };

  return (
    <div className="notification-overlay" onClick={showCancel ? handleCancel : undefined}>
      <div className="notification-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          {getIcon()}
          {title && <h3 className="dialog-title">{title}</h3>}
        </div>
        
        <div className="dialog-content">
          <p className="dialog-message">{message}</p>
        </div>
        
        <div className="dialog-actions">
          <button 
            className="dialog-btn confirm-btn"
            onClick={handleConfirm}
          >
            {confirmText}
          </button>
          {showCancel && (
            <button 
              className="dialog-btn cancel-btn"
              onClick={handleCancel}
            >
              {cancelText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationDialog;
