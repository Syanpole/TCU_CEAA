import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import Privacy from './components/Privacy';
import Modal from './components/Modal';
import LoginModal from './components/LoginModal';
import StudentRegistrationModal from './components/StudentRegistrationModal';
import Header from './components/Header';
import Dashboard from './components/AdminDashboard';
import StudentDashboard from './components/StudentDashboard';
import ProfileSettings from './components/ProfileSettings';
import StudentsManagement from './components/StudentsManagement';
import DocumentsManagement from './components/DocumentsManagement';
import GradesManagement from './components/GradesManagement';
import ApplicationsManagement from './components/ApplicationsManagement';
import './App.css';

const AppContent: React.FC = () => {
  const { user, loading, isAdmin } = useAuth();
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegistrationModal, setShowRegistrationModal] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' or 'profile'

  const showPrivacyPage = () => {
    setShowPrivacy(true);
  };

  const handleBackToLanding = () => {
    setShowPrivacy(false);
  };

  const handleLoginClick = () => {
    setShowLoginModal(true);
  };

  const handleRegisterClick = () => {
    setShowRegistrationModal(true);
  };

  const closeLoginModal = () => {
    setShowLoginModal(false);
  };

  const closeRegistrationModal = () => {
    setShowRegistrationModal(false);
  };

  const switchToRegistration = () => {
    setShowLoginModal(false);
    setShowRegistrationModal(true);
  };

  const switchToLogin = () => {
    setShowRegistrationModal(false);
    setShowLoginModal(true);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <div className="loading-text">Initializing application...</div>
      </div>
    );
  }

  if (!user) {
    if (showPrivacy) {
      return <Privacy onBackToHome={handleBackToLanding} />;
    }
    
    return (
      <>
        <LandingPage 
          onLoginClick={handleLoginClick}
          onRegisterClick={handleRegisterClick}
          onPrivacyClick={showPrivacyPage}
        />
        
        <Modal isOpen={showLoginModal} onClose={closeLoginModal}>
          <LoginModal 
            onStudentRegister={switchToRegistration}
            onClose={closeLoginModal}
          />
        </Modal>
        
        <Modal isOpen={showRegistrationModal} onClose={closeRegistrationModal}>
          <StudentRegistrationModal 
            onBack={closeRegistrationModal}
            onGoToLogin={switchToLogin}
            onClose={closeRegistrationModal}
          />
        </Modal>
      </>
    );
  }

  // For students, don't show the Header as StudentDashboard has its own integrated sidebar
  if (!isAdmin) {
    return (
      <div className="app-authenticated">
        {currentView === 'dashboard' ? (
          <StudentDashboard />
        ) : currentView === 'profile' ? (
          <ProfileSettings />
        ) : (
          <StudentDashboard />
        )}
      </div>
    );
  }

  // For admins, show the Header with navigation
  return (
    <div className="app-authenticated">
      <Header 
        currentView={currentView}
        onViewChange={setCurrentView}
      />
      {currentView === 'dashboard' ? (
        <Dashboard onViewChange={setCurrentView} />
      ) : currentView === 'profile' ? (
        <ProfileSettings />
      ) : currentView === 'students' ? (
        <StudentsManagement onViewChange={setCurrentView} />
      ) : currentView === 'documents' ? (
        <DocumentsManagement onViewChange={setCurrentView} />
      ) : currentView === 'grades' ? (
        <GradesManagement onViewChange={setCurrentView} />
      ) : currentView === 'applications' ? (
        <ApplicationsManagement onViewChange={setCurrentView} />
      ) : (
        <Dashboard onViewChange={setCurrentView} />
      )}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AppContent />
      </div>
    </AuthProvider>
  );
}

export default App;
