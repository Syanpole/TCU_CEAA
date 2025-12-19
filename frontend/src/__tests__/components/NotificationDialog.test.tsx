import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import NotificationDialog from '../../components/NotificationDialog';

describe('NotificationDialog Component', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  it('renders success notification', () => {
    render(
      <NotificationDialog
        isOpen={true}
        type="success"
        title="Success"
        message="Operation completed successfully"
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Operation completed successfully')).toBeInTheDocument();
  });

  it('renders error notification', () => {
    render(
      <NotificationDialog
        isOpen={true}
        type="error"
        title="Error"
        message="Something went wrong"
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('renders warning notification', () => {
    render(
      <NotificationDialog
        isOpen={true}
        type="warning"
        title="Warning"
        message="Please be careful"
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Warning')).toBeInTheDocument();
    expect(screen.getByText('Please be careful')).toBeInTheDocument();
  });

  it('renders info notification', () => {
    render(
      <NotificationDialog
        isOpen={true}
        type="info"
        title="Information"
        message="Here is some info"
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Information')).toBeInTheDocument();
    expect(screen.getByText('Here is some info')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    const { container } = render(
      <NotificationDialog
        isOpen={false}
        type="success"
        title="Test"
        message="Test message"
        onClose={mockOnClose}
      />
    );

    expect(container.firstChild).toBeNull();
  });
});
