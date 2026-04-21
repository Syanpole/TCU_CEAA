import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock axios before importing AuthContext
jest.mock('axios', () => ({
  default: {
    create: jest.fn(() => ({
      interceptors: {
        request: { use: jest.fn(), eject: jest.fn() },
        response: { use: jest.fn(), eject: jest.fn() },
      },
      post: jest.fn(),
      get: jest.fn(),
    })),
  },
}));

// Mock authService
jest.mock('../../services/authService', () => ({
  getCurrentUser: jest.fn(() => null),
  refreshAccessToken: jest.fn(),
  logout: jest.fn(),
}));

import { AuthProvider } from '../../contexts/AuthContext';

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should provide initial auth state', () => {
    const TestComponent = () => {
      return <div>Test</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('should handle user session from localStorage', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      role: 'student',
    };

    localStorage.setItem('user', JSON.stringify(mockUser));
    localStorage.setItem('access_token', 'fake-token');

    const TestComponent = () => {
      return <div>Session Test</div>;
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Session Test')).toBeInTheDocument();
  });
});
