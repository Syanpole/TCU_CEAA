import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LogoutModal from './LogoutModal';
import { 
  DashboardIcon, 
  DocumentIcon, 
  GradeIcon, 
  ApplicationIcon, 
  SettingsIcon, 
  LogoutIcon,
} from './Icons';
import './Sidebar.css';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  darkMode: boolean;
  isMobileMenuOpen?: boolean;
  onMobileMenuToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange, darkMode, isMobileMenuOpen, onMobileMenuToggle }) => {
  const { user, logout } = useAuth();
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const menuItems = [
    {
      id: 'overview',
      label: 'Overview',
      icon: <DashboardIcon size={18} />
    },
    {
      id: 'application',
      label: 'Application',
      icon: <ApplicationIcon size={18} />
    },
    {
      id: 'requirements',
      label: 'Submission of Requirements',
      icon: <DocumentIcon size={18} />
    },
    {
      id: 'grades',
      label: 'Grades',
      icon: <GradeIcon size={18} />
    },
    {
      id: 'application-details',
      label: 'Application Details',
      icon: <ApplicationIcon size={18} />
    }
  ];

  return (
    <div className={`sidebar ${darkMode ? 'dark-theme' : 'light-theme'} ${isMobileMenuOpen ? 'mobile-open' : ''} ${isMinimized ? 'minimized' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          <img src="/images/TCU_logo.png" alt="TCU Logo" className="tcu-logo" />
          {!isMinimized && <div className="logo-text">Student Portal</div>}
        </div>
        {!isMinimized && <div className="welcome-text">Welcome back!</div>}
        <button 
          className="sidebar-minimizer-btn"
          onClick={toggleMinimize}
          title={isMinimized ? 'Expand sidebar' : 'Minimize sidebar'}
        >
          {isMinimized ? (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2"/>
              <rect x="4" y="4" width="5" height="16" rx="1" fill="currentColor" fillOpacity="0.3"/>
              <path d="M13 9L16 12L13 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" strokeWidth="2"/>
              <rect x="4" y="4" width="5" height="16" rx="1" fill="currentColor" fillOpacity="0.3"/>
              <path d="M16 9L13 12L16 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
        </button>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => onSectionChange(item.id)}
            title={isMinimized ? item.label : ''}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {!isMinimized && <span className="sidebar-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          className="sidebar-item sidebar-profile-button"
          onClick={() => onSectionChange('profile')}
          title={isMinimized ? 'Profile Settings' : ''}
        >
          <span className="sidebar-icon">
            <SettingsIcon size={20} />
          </span>
          {!isMinimized && <span className="sidebar-label">Profile Settings</span>}
        </button>
        
        <button 
          className="sidebar-item sidebar-logout-button"
          onClick={() => setShowLogoutModal(true)}
          title={isMinimized ? 'Logout' : ''}
        >
          <span className="sidebar-icon">
            <LogoutIcon size={18} />
          </span>
          {!isMinimized && <span className="sidebar-label">Logout</span>}
        </button>
      </div>

      <LogoutModal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        onConfirm={() => {
          logout();
          setShowLogoutModal(false);
        }}
        userName={user?.first_name ? `${user.first_name} ${user.last_name}` : undefined}
      />
    </div>
  );
};

export default Sidebar;