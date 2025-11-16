// Device detection utility for mobile/desktop differentiation and camera access

export interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  os: 'iOS' | 'Android' | 'Windows' | 'MacOS' | 'Linux' | 'Unknown';
  hasCameraSupport: boolean;
  userAgent: string;
}

/**
 * Detect the current device type and capabilities
 */
export const detectDevice = (): DeviceInfo => {
  const userAgent = navigator.userAgent.toLowerCase();
  
  // Detect mobile devices
  const isMobileDevice = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
  
  // Detect tablets specifically (larger screen mobile devices)
  const isTabletDevice = /(ipad|tablet|playbook|silk)|(android(?!.*mobile))/i.test(userAgent);
  
  // Desktop is anything that's not mobile
  const isDesktopDevice = !isMobileDevice && !isTabletDevice;
  
  // Detect OS
  let os: DeviceInfo['os'] = 'Unknown';
  if (/iphone|ipad|ipod/i.test(userAgent)) {
    os = 'iOS';
  } else if (/android/i.test(userAgent)) {
    os = 'Android';
  } else if (/windows/i.test(userAgent)) {
    os = 'Windows';
  } else if (/mac/i.test(userAgent)) {
    os = 'MacOS';
  } else if (/linux/i.test(userAgent)) {
    os = 'Linux';
  }
  
  // Check if camera/media devices are supported
  const hasCameraSupport = !!(
    navigator.mediaDevices && 
    navigator.mediaDevices.getUserMedia
  );
  
  return {
    isMobile: isMobileDevice,
    isTablet: isTabletDevice,
    isDesktop: isDesktopDevice,
    os,
    hasCameraSupport,
    userAgent
  };
};

/**
 * Check camera permission status
 */
export const checkCameraPermission = async (): Promise<'granted' | 'denied' | 'prompt' | 'unsupported'> => {
  try {
    // Check if Permissions API is supported
    if (!navigator.permissions) {
      return 'unsupported';
    }
    
    const result = await navigator.permissions.query({ name: 'camera' as PermissionName });
    return result.state as 'granted' | 'denied' | 'prompt';
  } catch (error) {
    console.warn('Camera permission check failed:', error);
    return 'unsupported';
  }
};

/**
 * Request camera access and return the media stream
 * Automatically detects device type and uses appropriate camera
 */
export const requestCameraAccess = async (): Promise<MediaStream | null> => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error('Camera API not supported');
      return null;
    }
    
    // Detect device to choose appropriate camera
    const deviceInfo = detectDevice();
    
    // For liveness detection, we want front-facing camera (selfie mode)
    // Desktop: 'user' is the webcam
    // Mobile: 'user' is the front camera (selfie), 'environment' is back camera
    const constraints: MediaStreamConstraints = {
      video: {
        facingMode: 'user', // Front camera for selfies/face verification
        width: { ideal: 1280, max: 1920 },
        height: { ideal: 720, max: 1080 }
      },
      audio: false
    };
    
    console.log(`Requesting camera access on ${deviceInfo.os} (${deviceInfo.isMobile ? 'Mobile' : 'Desktop'})`);
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    
    console.log('Camera access granted:', {
      videoTracks: stream.getVideoTracks().length,
      settings: stream.getVideoTracks()[0]?.getSettings()
    });
    
    return stream;
  } catch (error: any) {
    console.error('Camera access failed:', error);
    
    // Log specific error for debugging
    if (error.name === 'NotAllowedError') {
      console.error('Camera permission denied by user');
    } else if (error.name === 'NotFoundError') {
      console.error('No camera device found');
    } else if (error.name === 'NotReadableError') {
      console.error('Camera is already in use by another application');
    } else if (error.name === 'OverconstrainedError') {
      console.error('Camera constraints could not be satisfied');
    }
    
    return null;
  }
};
