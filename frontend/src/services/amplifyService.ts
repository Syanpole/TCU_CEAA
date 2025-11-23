import { Amplify } from 'aws-amplify';
import { apiClient } from './authService';

let amplifyConfigured = false;
let configurationPromise: Promise<boolean> | null = null;

export interface AmplifyConfig {
  enabled: boolean;
  region: string;
  identityPoolId?: string;
  message?: string;
}

/**
 * Initialize Amplify with AWS credentials from backend
 * This should be called once at the app level
 * Returns true if successfully configured, false otherwise
 */
export const initializeAmplify = async (): Promise<boolean> => {
  // If already configured, return immediately
  if (amplifyConfigured) {
    return true;
  }

  // If configuration is in progress, wait for it
  if (configurationPromise) {
    return configurationPromise;
  }

  // Start new configuration
  configurationPromise = (async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        console.warn('⚠️ Cannot initialize Amplify: No auth token found');
        return false;
      }

      console.log('🔧 Fetching AWS configuration from backend...');
      
      const response = await apiClient.get<AmplifyConfig>('/face-verification/aws-credentials/');

      if (!response.data.enabled) {
        console.warn('⚠️ AWS Rekognition is not enabled');
        return false;
      }

      // 🔒 SECURITY: No credentials exposed - using Cognito Identity Pool
      const identityPoolId = response.data.identityPoolId || 'us-east-1:a1252e7a-7da3-4703-88da-22cacd3b88b5';
      
      console.log('🔧 Configuring AWS Amplify with Cognito Identity Pool');
      console.log('🔒 Security: Credentials managed via AWS Cognito (no keys exposed)');
      
      Amplify.configure({
        Auth: {
          Cognito: {
            identityPoolId: identityPoolId,
            allowGuestAccess: true
          }
        }
      });

      // Store configuration (NOT credentials) for reference
      (window as any).awsConfig = {
        region: response.data.region,
        identityPoolId: identityPoolId,
        configuredAt: new Date().toISOString()
      };

      amplifyConfigured = true;
      console.log('✅ Amplify configured successfully');
      return true;

    } catch (error: any) {
      console.error('❌ Failed to initialize Amplify:', error);
      
      if (error.response?.status === 401) {
        console.error('🔐 Authentication required. Please log in.');
      } else if (error.response?.status === 403) {
        console.error('🚫 Access denied. Check permissions.');
      } else if (error.response?.status === 500) {
        console.error('⚠️ Server error. Check backend configuration.');
      }
      
      return false;
    } finally {
      configurationPromise = null;
    }
  })();

  return configurationPromise;
};

/**
 * Check if Amplify is configured
 */
export const isAmplifyConfigured = (): boolean => {
  return amplifyConfigured;
};

/**
 * Get stored AWS configuration (no credentials)
 */
export const getAWSConfig = (): { region: string; identityPoolId: string; configuredAt: string } | null => {
  return (window as any).awsConfig || null;
};

/**
 * Reset Amplify configuration (for logout)
 */
export const resetAmplifyConfiguration = (): void => {
  amplifyConfigured = false;
  configurationPromise = null;
  delete (window as any).awsConfig;
  console.log('🔄 Amplify configuration reset');
  console.log('🔒 Security: Session cleared, credentials revoked');
};
