import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LogoutModal from './LogoutModal';
import { 
  DashboardIcon, 
  DocumentIcon, 
  GradeIcon, 
  ApplicationIcon, 
  RequirementsIcon, 
  SettingsIcon, 
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

  const menuItems = [
    {
      id: 'overview',
      label: 'Overview',
      icon: <DashboardIcon size={20} />
    },
    {
      id: 'documents',
      label: 'Documents',
      icon: <DocumentIcon size={20} />
    },
    {
      id: 'grades',
      label: 'Grades',
      icon: <GradeIcon size={20} />
    },
    {
      id: 'application-details',
      label: 'Application Details',
      icon: <ApplicationIcon size={20} />
    }
  ];

  return (
    <div className={`sidebar ${darkMode ? 'dark-theme' : 'light-theme'} ${isMobileMenuOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-text">Student Portal</div>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => onSectionChange(item.id)}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button
          className="sidebar-item sidebar-profile-button"
          onClick={() => onSectionChange('profile')}
        >
          <span className="sidebar-icon">
            <SettingsIcon size={20} />
          </span>
          <span className="sidebar-label">Profile Settings</span>
        </button>
        
        <button 
          className="sidebar-item sidebar-logout-button"
          onClick={() => setShowLogoutModal(true)}
        >
          <span className="sidebar-label">Logout</span>
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