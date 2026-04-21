import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import ModernLoadingSpinner from '../../components/ModernLoadingSpinner';

describe('ModernLoadingSpinner Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<ModernLoadingSpinner />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(<ModernLoadingSpinner />);
    const spinner = container.querySelector('.modern-loading-container');
    expect(spinner).toBeInTheDocument();
  });

  it('renders loading animation elements', () => {
    const { container } = render(<ModernLoadingSpinner />);
    expect(container.querySelector('.modern-spinner')).toBeInTheDocument();
  });
});
