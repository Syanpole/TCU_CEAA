/**
 * Email Verification Service
 * Handles sending and validating email verification codes
 */

import emailjs from '@emailjs/browser';

interface VerificationEmailParams {
  toEmail: string;
  verificationCode: string;
}

interface EmailResponse {
  success: boolean;
  message: string;
}

class VerificationService {
  private readonly SERVICE_ID = process.env.REACT_APP_EMAILJS_SERVICE_ID || '';
  private readonly VERIFICATION_TEMPLATE_ID = process.env.REACT_APP_EMAILJS_VERIFICATION_TEMPLATE_ID || '';
  private readonly PUBLIC_KEY = process.env.REACT_APP_EMAILJS_PUBLIC_KEY || '';

  /**
   * Send verification code email via EmailJS
   */
  async sendVerificationEmail({ toEmail, verificationCode }: VerificationEmailParams): Promise<EmailResponse> {
    try {
      // Validate inputs
      if (!toEmail || !verificationCode) {
        return {
          success: false,
          message: 'Email and verification code are required'
        };
      }

      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(toEmail)) {
        return {
          success: false,
          message: 'Invalid email format'
        };
      }

      // Validate code is 6 digits
      if (!/^\d{6}$/.test(verificationCode)) {
        return {
          success: false,
          message: 'Verification code must be 6 digits'
        };
      }

      console.log('📧 Sending verification code to:', toEmail);

      // Prepare template parameters
      const templateParams = {
        to_email: toEmail,
        verification_code: verificationCode,
        from_name: 'TCU-CEAA System',
        reply_to: 'ceaainfo@tcu.edu.ph'
      };

      // Send email via EmailJS
      const response = await emailjs.send(
        this.SERVICE_ID,
        this.VERIFICATION_TEMPLATE_ID,
        templateParams,
        this.PUBLIC_KEY
      );

      if (response.status === 200) {
        console.log('✅ Verification email sent successfully');
        return {
          success: true,
          message: `Verification code sent to ${toEmail}`
        };
      } else {
        console.error('❌ EmailJS response status:', response.status);
        return {
          success: false,
          message: 'Failed to send verification email. Please try again.'
        };
      }

    } catch (error: any) {
      console.error('❌ Error sending verification email:', error);
      
      // Handle specific EmailJS errors
      if (error.text) {
        return {
          success: false,
          message: `Email service error: ${error.text}`
        };
      }

      return {
        success: false,
        message: 'An unexpected error occurred while sending verification email'
      };
    }
  }

  /**
   * Validate configuration
   */
  isConfigured(): boolean {
    const configured = !!(this.SERVICE_ID && this.VERIFICATION_TEMPLATE_ID && this.PUBLIC_KEY);
    if (!configured) {
      console.warn('⚠️ EmailJS verification service not fully configured');
    }
    return configured;
  }
}

// Export singleton instance
export const verificationService = new VerificationService();

// Also export the class for testing
export default VerificationService;
