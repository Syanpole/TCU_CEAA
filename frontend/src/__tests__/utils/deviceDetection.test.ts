import { detectDevice } from '../../utils/deviceDetection';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('deviceDetection', () => {
  beforeEach(() => {
    // Reset mocks
    (window.matchMedia as jest.Mock).mockClear();
  });

  it('should detect device info', () => {
    const deviceInfo = detectDevice();
    
    expect(deviceInfo).toHaveProperty('isMobile');
    expect(deviceInfo).toHaveProperty('isTablet');
    expect(deviceInfo).toHaveProperty('isDesktop');
    expect(deviceInfo).toHaveProperty('os');
    expect(deviceInfo).toHaveProperty('hasCameraSupport');
  });

  it('should detect desktop by default in test environment', () => {
    const deviceInfo = detectDevice();
    
    // In test environment, should detect as desktop
    expect(deviceInfo.isDesktop).toBe(true);
    expect(deviceInfo.isMobile).toBe(false);
  });

  it('should have userAgent string', () => {
    const deviceInfo = detectDevice();
    
    expect(deviceInfo.userAgent).toBeDefined();
    expect(typeof deviceInfo.userAgent).toBe('string');
  });

  it('should detect OS', () => {
    const deviceInfo = detectDevice();
    
    expect(deviceInfo.os).toBeDefined();
    expect(['iOS', 'Android', 'Windows', 'MacOS', 'Linux', 'Unknown']).toContain(deviceInfo.os);
  });
});
