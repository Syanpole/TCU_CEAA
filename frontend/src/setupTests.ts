// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock AWS SDK modules to avoid transformation issues with static class blocks
jest.mock('@aws-amplify/ui-react-liveness', () => ({
  FaceLivenessDetector: jest.fn(() => null),
}));

jest.mock('aws-amplify', () => ({
  Amplify: {
    configure: jest.fn(),
  },
}));

jest.mock('@aws-sdk/client-rekognitionstreaming', () => ({}));

// Mock IntersectionObserver for tests
(global as any).IntersectionObserver = class IntersectionObserver {
  constructor(_callback: IntersectionObserverCallback, _options?: IntersectionObserverInit) {
    // Mock implementation - parameters intentionally unused
  }
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
};
