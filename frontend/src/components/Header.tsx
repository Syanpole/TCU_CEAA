import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LogoutModal from './LogoutModal';
import './Header.css';

const Header: React.FC = () => {
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
          <h1 className="header-title">TCU CEAA {isAdmin ? 'Dashboard' : 'Student Portal'}</h1>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <span className="user-name">
              {user?.first_name} {user?.last_name}
            </span>
            <span className={`user-role ${getRoleClass()}`}>
              {getRoleDisplay()}
            </span>
            {user?.role === 'student' && user?.student_id && (
              <span className="student-id">
                #{user.student_id}
              </span>
            )}
          </div>
          
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
