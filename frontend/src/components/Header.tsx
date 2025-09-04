import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LogoutModal from './LogoutModal';
import DefaultAvatar from './DefaultAvatar';
import './Header.css';

interface HeaderProps {
  currentView?: string;
  onViewChange?: (view: string) => void;
}

const Header: React.FC<HeaderProps> = ({ currentView = 'dashboard', onViewChange }) => {
  const { user, logout, isAdmin } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const handleLogoutClick = () => {
    setShowLogoutModal(true);
  };

  const handleLogoutConfirm = () => {
    logout();
    setShowLogoutModal(false);
  };

  const handleLogoutCancel = () => {
    setShowLogoutModal(false);
  };

  const getRoleDisplay = () => {
    if (isAdmin) return 'ADMIN';
    if (user?.role === 'student') return 'STUDENT';
    return 'USER';
  };

  const getRoleClass = () => {
    if (isAdmin) return 'admin';
    if (user?.role === 'student') return 'student';
    return 'user';
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <h1 
            className="header-title clickable"
            onClick={() => onViewChange && onViewChange('dashboard')}
          >
            TCU-CEAA {isAdmin ? 'Dashboard' : 'Student Portal'}
          </h1>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <div className="user-avatar">
              {user?.profile_image_url ? (
                <img 
                  src={user.profile_image_url} 
                  alt="Profile" 
                  className="user-avatar-image"
                />
              ) : (
                <DefaultAvatar 
                  firstName={user?.first_name}
                  lastName={user?.last_name}
                  size={40}
                  className="user-avatar-default"
                />
              )}
            </div>
            <div className="user-details">
              <span className="user-name">
                {user?.first_name} {user?.last_name}
              </span>
              <span className={`user-role ${getRoleClass()}`}>
                {getRoleDisplay()}
              </span>
            </div>
          </div>
          
          {onViewChange && (
            <button 
              className={`profile-button ${currentView === 'profile' ? 'active' : ''}`}
              onClick={() => onViewChange('profile')}
            >
              Profile
            </button>
          )}
          
          <button 
            onClick={handleLogoutClick}
            className="logout-button"
          >
            Logout
          </button>
        </div>
      </div>
      
      <LogoutModal
        isOpen={showLogoutModal}
        onClose={handleLogoutCancel}
        onConfirm={handleLogoutConfirm}
        userName={user?.first_name ? `${user.first_name} ${user.last_name}` : undefined}
      />
    </header>
  );
};

export default Header;
