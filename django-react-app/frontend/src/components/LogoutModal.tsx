import React from 'react';
import './LogoutModal.css';

interface LogoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  userName?: string;
}

const LogoutModal: React.FC<LogoutModalProps> = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  userName 
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="logout-modal-backdrop" onClick={handleBackdropClick}>
      <div className="logout-modal">
        <div className="logout-modal-header">
          <div className="logout-icon">
            <svg 
              width="24" 
              height="24" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                d="M17 7L9.5 14.5L6.5 11.5" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h3 className="logout-modal-title">Confirm Logout</h3>
        </div>
        
        <div className="logout-modal-body">
          <p className="logout-message">
            {userName ? (
              <>
                Are you sure you want to log out, <strong>{userName}</strong>?
              </>
            ) : (
              'Are you sure you want to log out?'
            )}
          </p>
          <p className="logout-submessage">
            You will need to enter your credentials again to access the dashboard.
          </p>
        </div>
        
        <div className="logout-modal-actions">
          <button 
            type="button"
            className="logout-cancel-btn"
            onClick={onClose}
          >
            Cancel
          </button>
          <button 
            type="button"
            className="logout-confirm-btn"
            onClick={onConfirm}
          >
            <span className="logout-btn-icon">
              <svg 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path 
                  d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
                <path 
                  d="M16 17L21 12L16 7" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
                <path 
                  d="M21 12H9" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default LogoutModal;
