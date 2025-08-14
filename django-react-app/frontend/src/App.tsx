import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import './App.css';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
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
      <Login 
        onToggleMode={toggleMode} 
        isRegisterMode={isRegisterMode} 
      />
    );
  }

  return (
    <div className="app-authenticated">
      <Header />
      <Dashboard />
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
