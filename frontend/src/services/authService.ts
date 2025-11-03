import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'user' | 'student';
  first_name: string;
  last_name: string;
  middle_initial?: string;
  student_id?: string;
  profile_image_url?: string;
  created_at: string;
}

export interface LoginResponse {
  token: string;
  user: User;
  message: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  middle_initial?: string;
  role?: 'admin' | 'user' | 'student';
  student_id?: string;
}

export interface ProfileImageResponse {
  message: string;
  profile_image?: string;
}

export interface VerifyStudentResponse {
  verified: boolean;
  message: string;
  student_data?: {
    student_id: string;
    first_name: string;
    last_name: string;
    middle_initial: string;
    sex: string;
    course: string;
    year: number;
  };
}

// Create axios instance with interceptor for authentication
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export const authService = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/login/`, {
      username,
      password,
    });
    return response.data;
  },

  verifyStudent: async (studentData: {
    studentId: string;
    firstName: string;
    lastName: string;
    middleInitial: string;
  }): Promise<VerifyStudentResponse> => {
    const response = await axios.post<VerifyStudentResponse>(`${API_BASE_URL}/auth/verify-student/`, {
      student_id: studentData.studentId,
      first_name: studentData.firstName,
      last_name: studentData.lastName,
      middle_initial: studentData.middleInitial,
    });
    return response.data;
  },

  register: async (userData: RegisterData): Promise<LoginResponse> => {
    const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/register/`, userData);
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/profile/');
    return response.data;
  },

  checkAdmin: async (): Promise<{ is_admin: boolean; role: string }> => {
    const response = await apiClient.get<{ is_admin: boolean; role: string }>('/auth/check-admin/');
    return response.data;
  },
};

export { apiClient };
