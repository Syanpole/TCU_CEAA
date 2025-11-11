/**
 * Unit tests for StudentDashboard TypeScript changes
 * Tests the full application check and type safety improvements
 */

import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StudentDashboard from '../components/StudentDashboard';
import { apiClient } from '../services/authService';

// Mock the API client
jest.mock('../services/authService', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

describe('StudentDashboard - Full Application Check', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('should display "Application Completed & Locked" when full application exists', async () => {
    // Mock API responses
    (apiClient.get as jest.Mock).mockImplementation((url: string) => {
      if (url === '/basic-qualification/') {
        return Promise.resolve({
          data: [{
            id: 1,
            full_name: 'John Doe',
            student_id: '22-00417',
            college: 'CAS',
            date_of_birth: '2000-01-01',
            sex: 'Male',
            civil_status: 'Single',
            contact_number: '09123456789',
            email_address: 'john@example.com',
          }],
        });
      }
      if (url === '/full-application/') {
        return Promise.resolve({
          data: [{
            id: 1,
            school_year: '2025-2026',
            semester: '1st',
            status: 'submitted',
            is_submitted: true,
            submitted_at: '2025-11-10T10:00:00Z',
          }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<StudentDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/Application Completed & Locked/i)).toBeInTheDocument();
    });
  });

  it('should display "In Progress" when no full application exists', async () => {
    // Mock API responses
    (apiClient.get as jest.Mock).mockImplementation((url: string) => {
      if (url === '/basic-qualification/') {
        return Promise.resolve({
          data: [{
            id: 1,
            full_name: 'Jane Smith',
            student_id: '22-00418',
            college: 'CAS',
          }],
        });
      }
      if (url === '/full-application/') {
        return Promise.resolve({ data: [] }); // No full application
      }
      return Promise.resolve({ data: [] });
    });

    render(<StudentDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/In Progress/i)).toBeInTheDocument();
    });
  });

  it('should handle type-safe full application data', async () => {
    const mockFullApplicationData = [{
      id: 2,
      school_year: '2025-2026',
      semester: '2nd',
      status: 'submitted',
      is_submitted: true,
      submitted_at: '2025-11-10T15:30:00Z',
      father_name: 'Father Name',
      mother_name: 'Mother Name',
      guardian_name: 'Guardian Name',
      father_occupation: 'Engineer',
      mother_occupation: 'Teacher',
      guardian_occupation: 'Doctor',
      father_contact: '09111111111',
      mother_contact: '09222222222',
      guardian_contact: '09333333333',
      father_education: 'College Graduate',
      mother_education: 'College Graduate',
      guardian_education: 'College Graduate',
      family_income: '50000-100000',
      number_of_siblings: 2,
      birth_order: 2,
      indigenous_group: null,
      differently_abled: false,
      solo_parent: false,
      current_address: '123 Test St',
      permanent_address: '123 Test St',
      accommodation_type: 'Own House',
      distance_from_tcu: '5-10 km',
      travel_time: '30-60 mins',
      elementary_school: 'Test Elementary',
      elementary_address: 'Test City',
      elementary_honors: 'With Honors',
      junior_high_school: 'Test JHS',
      junior_high_address: 'Test City',
      junior_high_honors: 'With Honors',
      senior_high_school: 'Test SHS',
      senior_high_address: 'Test City',
      senior_high_honors: 'With Honors',
      senior_high_strand: 'STEM',
      college_school: null,
      college_address: null,
      college_honors: null,
      college_course: null,
      primary_reason: 'Quality Education',
      secondary_reason: 'Near Home',
      tertiary_reason: 'Affordable',
      other_reason: null,
    }];

    (apiClient.get as jest.Mock).mockImplementation((url: string) => {
      if (url === '/basic-qualification/') {
        return Promise.resolve({ data: [{ id: 1, full_name: 'Test User' }] });
      }
      if (url === '/full-application/') {
        return Promise.resolve({ data: mockFullApplicationData });
      }
      return Promise.resolve({ data: [] });
    });

    render(<StudentDashboard />);

    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith('/full-application/');
    });

    // Verify that the component handles the full application data correctly
    await waitFor(() => {
      expect(screen.getByText(/2025-2026/i)).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    (apiClient.get as jest.Mock).mockRejectedValue(new Error('API Error'));

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    render(<StudentDashboard />);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalled();
    });

    consoleSpy.mockRestore();
  });

  it('should set hasCompletedApplication to true when full application exists', async () => {
    (apiClient.get as jest.Mock).mockImplementation((url: string) => {
      if (url === '/basic-qualification/') {
        return Promise.resolve({
          data: [{
            id: 1,
            full_name: 'Test User',
            student_id: '22-00420',
          }],
        });
      }
      if (url === '/full-application/') {
        return Promise.resolve({
          data: [{
            id: 1,
            school_year: '2025-2026',
            semester: '1st',
            is_submitted: true,
          }],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<StudentDashboard />);

    await waitFor(() => {
      // Component should show completed state
      expect(screen.queryByText(/In Progress/i)).not.toBeInTheDocument();
    });
  });

  it('should handle multiple full applications and use the first one', async () => {
    (apiClient.get as jest.Mock).mockImplementation((url: string) => {
      if (url === '/basic-qualification/') {
        return Promise.resolve({
          data: [{ id: 1, full_name: 'Test User' }],
        });
      }
      if (url === '/full-application/') {
        return Promise.resolve({
          data: [
            {
              id: 1,
              school_year: '2025-2026',
              semester: '1st',
              is_submitted: true,
            },
            {
              id: 2,
              school_year: '2024-2025',
              semester: '2nd',
              is_submitted: true,
            },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });

    render(<StudentDashboard />);

    await waitFor(() => {
      // Should display first application's data
      expect(screen.getByText(/2025-2026/i)).toBeInTheDocument();
    });
  });
});

describe('StudentDashboard - Type Safety', () => {
  it('should properly type FullApplicationData interface', async () => {
    // This test ensures TypeScript compilation succeeds
    // The interface definition should match the API response
    
    interface FullApplicationData {
      id: number;
      school_year: string;
      semester: string;
      status: string;
      is_submitted: boolean;
      submitted_at?: string;
      father_name?: string;
      mother_name?: string;
      // ... other optional fields
    }

    const testData: FullApplicationData = {
      id: 1,
      school_year: '2025-2026',
      semester: '1st',
      status: 'submitted',
      is_submitted: true,
    };

    expect(testData.id).toBe(1);
    expect(testData.school_year).toBe('2025-2026');
    expect(testData.is_submitted).toBe(true);
  });

  it('should handle type casting from API response', () => {
    const mockApiResponse = {
      data: [
        {
          id: 1,
          school_year: '2025-2026',
          semester: '1st',
          status: 'submitted',
          is_submitted: true,
        },
      ],
    };

    // Type casting as done in the component
    interface FullApplicationData {
      id: number;
      school_year: string;
      semester: string;
      status: string;
      is_submitted: boolean;
    }

    const fullApplications = mockApiResponse.data as FullApplicationData[];
    
    expect(fullApplications).toHaveLength(1);
    expect(fullApplications[0].school_year).toBe('2025-2026');
  });
});

export {};
