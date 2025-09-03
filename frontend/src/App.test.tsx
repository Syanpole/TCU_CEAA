import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the auth context
jest.mock('./contexts/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    user: null,
    loading: false,
    isAdmin: false,
    login: jest.fn(),
    logout: jest.fn(),
  }),
}));

test('renders landing page', () => {
  render(<App />);
  const linkElement = screen.getAllByText(/TCU CEAA Portal/i)[0];
  expect(linkElement).toBeInTheDocument();
});
