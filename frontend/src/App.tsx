import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import Login from './components/Login';
import Header from './components/Header';
import Dashboard from './components/AdminDashboard';
import StudentDashboard from './components/StudentDashboard';
import StudentRegistration from './components/StudentRegistration';
import ProfileSettings from './components/ProfileSettings';
import StudentsManagement from './components/StudentsManagement';
import DocumentsManagement from './components/DocumentsManagement';
import GradesManagement from './components/GradesManagement';
import ApplicationsManagement from './components/ApplicationsManagement';
import Analytics from './components/Analytics';
import './App.css';

const AppContent: React.FC = () => {
  const { user, loading, isAdmin } = useAuth();
  const [showLanding, setShowLanding] = useState(true);
  const [showStudentRegistration, setShowStudentRegistration] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' or 'profile'

  const showStudentRegister = () => {
    setShowStudentRegistration(true);
    setShowLanding(false);
  };

  const backToLanding = () => {
    setShowLanding(true);
    setShowStudentRegistration(false);
  };

  const goToLogin = () => {
    setShowLanding(false);
    setShowStudentRegistration(false);
  };

  const handleLoginClick = () => {
    // Login is now handled by modal, no state change needed
  };

  const handleRegisterClick = () => {
    // Registration is now handled by modal, no state change needed
  };

  const handleBackToLanding = () => {
    setShowLanding(true);
    setShowStudentRegistration(false);
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
    return (
      <LandingPage 
        onLoginClick={handleLoginClick}
        onRegisterClick={handleRegisterClick}
      />
    );
  }

  return (
    <div className="app-authenticated">
      <Header 
        currentView={currentView}
        onViewChange={setCurrentView}
      />
      {currentView === 'dashboard' ? (
        isAdmin ? <Dashboard onViewChange={setCurrentView} /> : <StudentDashboard />
      ) : currentView === 'profile' ? (
        <ProfileSettings />
      ) : currentView === 'students' && isAdmin ? (
        <StudentsManagement onViewChange={setCurrentView} />
      ) : currentView === 'documents' && isAdmin ? (
        <DocumentsManagement onViewChange={setCurrentView} />
      ) : currentView === 'grades' && isAdmin ? (
        <GradesManagement onViewChange={setCurrentView} />
      ) : currentView === 'applications' && isAdmin ? (
        <ApplicationsManagement onViewChange={setCurrentView} />
      ) : currentView === 'analytics' && isAdmin ? (
        <Analytics onViewChange={setCurrentView} />
      ) : (
        isAdmin ? <Dashboard onViewChange={setCurrentView} /> : <StudentDashboard />
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
