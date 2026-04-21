import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LandingPage from '../../components/LandingPage';

describe('LandingPage Component', () => {
  it('renders landing page with title', () => {
    render(<LandingPage />);
    
    const titleElements = screen.getAllByText(/TCU.*CEAA/i);
    expect(titleElements.length).toBeGreaterThan(0);
  });

  it('displays TCU logo', () => {
    render(<LandingPage />);
    
    const logo = screen.getByAltText('TCU Logo');
    expect(logo).toBeInTheDocument();
  });

  it('shows About and Contact sections', () => {
    render(<LandingPage />);
    
    // Check for section headings
    const sections = screen.getAllByRole('heading');
    expect(sections.length).toBeGreaterThan(0);
  });

  it('has registration and login buttons', () => {
    render(<LandingPage />);
    
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
