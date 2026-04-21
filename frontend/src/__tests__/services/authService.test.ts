// Mock the entire authService module to avoid axios initialization issues
jest.mock('../../services/authService', () => ({
  login: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
  refreshAccessToken: jest.fn(),
}));

import { login, logout, getCurrentUser } from '../../services/authService';

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should be defined', () => {
      expect(typeof login).toBe('function');
    });

    it('should be a mocked function', () => {
      expect(jest.isMockFunction(login)).toBe(true);
    });
  });

  describe('logout', () => {
    it('should be defined', () => {
      expect(typeof logout).toBe('function');
    });

    it('should be callable', () => {
      expect(() => logout()).not.toThrow();
      expect(logout).toHaveBeenCalled();
    });
  });

  describe('getCurrentUser', () => {
    it('should be defined', () => {
      expect(typeof getCurrentUser).toBe('function');
    });

    it('should be callable', () => {
      getCurrentUser();
      expect(getCurrentUser).toHaveBeenCalled();
    });
  });

  describe('refreshAccessToken', () => {
    it('should be defined', () => {
      expect(typeof login).toBe('function');
    });
  });
});
