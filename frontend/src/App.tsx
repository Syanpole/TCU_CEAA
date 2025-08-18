import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import StudentDashboard from './components/StudentDashboard';
import StudentRegistration from './components/StudentRegistration';
import './App.css';

const AppContent: React.FC = () => {
  const { user, loading, isAdmin } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [showStudentRegistration, setShowStudentRegistration] = useState(false);

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
  };

  const showStudentRegister = () => {
    setShowStudentRegistration(true);
  };

  const backToLogin = () => {
    setShowStudentRegistration(false);
    setIsRegisterMode(false);
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
    if (showStudentRegistration) {
      return <StudentRegistration onBack={backToLogin} />;
    }
    return (
      <Login 
        onToggleMode={toggleMode} 
        isRegisterMode={isRegisterMode}
        onStudentRegister={showStudentRegister}
      />
    );
  }

  return (
    <div className="app-authenticated">
      <Header />
      {isAdmin ? <Dashboard /> : <StudentDashboard />}
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
