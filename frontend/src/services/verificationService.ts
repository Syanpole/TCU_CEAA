import { apiClient } from './authService';

export interface VerificationResponse {
  success: boolean;
  message: string;
  email?: string;
  verified?: boolean;
  expired?: boolean;
  expires_in_minutes?: number;
  requires_verification?: boolean;
}

/**
 * Send verification code to email address
 * The code is sent directly from the backend via email - NEVER exposed to frontend for security
 */
export const sendVerificationCode = async (email: string): Promise<VerificationResponse> => {
  try {
    const response = await apiClient.post('/api/auth/send-verification-code/', { email });
    const data = response.data as any;
    
    return {
      success: true,
      message: data.message || 'Verification code sent to your email!',
      email: data.email,
      expires_in_minutes: data.expires_in_minutes || 10
    };
  } catch (error: any) {
    console.error('Error sending verification code:', error);
    
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.message || 
                        'Failed to send verification code. Please try again.';
    
    return {
      success: false,
      message: errorMessage
    };
  }
};

/**
 * Verify the code entered by user
 */
export const verifyEmailCode = async (email: string, code: string): Promise<VerificationResponse> => {
  try {
    const response = await apiClient.post('/api/auth/verify-email-code/', { email, code });
    const data = response.data as any;
    
    return {
      success: true,
      message: data.message || 'Email verified successfully!',
      email: data.email,
      verified: data.verified
    };
  } catch (error: any) {
    console.error('Error verifying code:', error);
    
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.message || 
                        'Verification failed. Please try again.';
    
    const expired = error.response?.data?.expired || false;
    
    return {
      success: false,
      message: errorMessage,
      expired
    };
  }
};

/**
 * Resend verification code to email
 * The code is sent directly from the backend via email - NEVER exposed to frontend for security
 */
export const resendVerificationCode = async (email: string): Promise<VerificationResponse> => {
  try {
    const response = await apiClient.post('/api/auth/resend-verification-code/', { email });
    const data = response.data as any;
    
    return {
      success: true,
      message: data.message || 'New verification code sent to your email!',
      email: data.email,
      expires_in_minutes: data.expires_in_minutes || 10
    };
  } catch (error: any) {
    console.error('Error resending verification code:', error);
    
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.message || 
                        'Failed to resend verification code. Please try again.';
    
    return {
      success: false,
      message: errorMessage
    };
  }
};

const verificationService = {
  sendVerificationCode,
  verifyEmailCode,
  resendVerificationCode
};

export default verificationService;
