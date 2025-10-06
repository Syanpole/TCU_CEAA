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
  
  // Check for the main portal title - use getAllByText and check first element
  const portalTitles = screen.getAllByText(/TCU.*CEAA.*Portal/i);
  expect(portalTitles.length).toBeGreaterThan(0);
  expect(portalTitles[0]).toBeInTheDocument();
  
  // Check for landing page specific class name
  const landingContainer = document.querySelector('.landing-container');
  expect(landingContainer).toBeInTheDocument();
  
  // Check for TCU Logo which is unique to landing page
  const tcuLogo = screen.getByAltText('TCU Logo');
  expect(tcuLogo).toBeInTheDocument();
});
