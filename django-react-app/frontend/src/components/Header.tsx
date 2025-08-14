import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Header.css';

const Header: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <h1 className="header-title">TCU CEAA Dashboard</h1>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <span className="user-name">
              {user?.first_name} {user?.last_name}
            </span>
            <span className={`user-role ${isAdmin ? 'admin' : 'user'}`}>
              {isAdmin ? 'Admin' : 'User'}
            </span>
          </div>
          
          <button 
            onClick={handleLogout}
            className="logout-button"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
