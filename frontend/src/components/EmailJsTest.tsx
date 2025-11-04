import React, { useState } from 'react';
import { sendApprovalEmail } from '../services/email/emailService';

/**
 * Simple Test Component for EmailJS
 * Use this to quickly test your EmailJS configuration
 */
const EmailJsTest: React.FC = () => {
  const [testEmail, setTestEmail] = useState('');
  const [testName, setTestName] = useState('');
  const [result, setResult] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!testEmail || !testName) {
      setResult({
        type: 'error',
        message: 'Please fill in both name and email',
      });
      return;
    }

    setLoading(true);
    setResult({
      type: 'info',
      message: 'Sending test email...',
    });

    try {
      const emailResult = await sendApprovalEmail(testName, testEmail);

      if (emailResult.success) {
        setResult({
          type: 'success',
          message: `✓ Success! Test email sent to ${testEmail}. Check your inbox (and spam folder).`,
        });
      } else {
        setResult({
          type: 'error',
          message: `✕ Failed: ${emailResult.message}`,
        });
      }
    } catch (error: any) {
      setResult({
        type: 'error',
        message: `✕ Error: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const checkConfiguration = () => {
    const serviceId = process.env.REACT_APP_EMAILJS_SERVICE_ID;
    const templateId = process.env.REACT_APP_EMAILJS_TEMPLATE_ID;
    const publicKey = process.env.REACT_APP_EMAILJS_PUBLIC_KEY;

    const issues: string[] = [];

    if (!serviceId || serviceId === 'service_xxxxxx') {
      issues.push('SERVICE_ID not configured');
    }
    if (!templateId || templateId === 'template_xxxxxx') {
      issues.push('TEMPLATE_ID not configured');
    }
    if (!publicKey || publicKey === 'AbCdEfG12345') {
      issues.push('PUBLIC_KEY not configured');
    }

    if (issues.length > 0) {
      setResult({
        type: 'error',
        message: `Configuration issues: ${issues.join(', ')}. Please update your .env file.`,
      });
    } else {
      setResult({
        type: 'success',
        message:
          '✓ Configuration looks good! You can now test sending an email.',
      });
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>📧 EmailJS Test Page</h1>
        <p style={styles.subtitle}>
          Test your EmailJS configuration and send a test approval email
        </p>

        <div style={styles.section}>
          <h3>Step 1: Check Configuration</h3>
          <button onClick={checkConfiguration} style={styles.checkButton}>
            Check .env Configuration
          </button>

          <div style={styles.configInfo}>
            <p>
              <strong>Current Configuration:</strong>
            </p>
            <code style={styles.code}>
              SERVICE_ID:{' '}
              {process.env.REACT_APP_EMAILJS_SERVICE_ID || 'Not set'}
            </code>
            <code style={styles.code}>
              TEMPLATE_ID:{' '}
              {process.env.REACT_APP_EMAILJS_TEMPLATE_ID || 'Not set'}
            </code>
            <code style={styles.code}>
              PUBLIC_KEY:{' '}
              {process.env.REACT_APP_EMAILJS_PUBLIC_KEY
                ? '✓ Set'
                : 'Not set'}
            </code>
          </div>
        </div>

        <div style={styles.section}>
          <h3>Step 2: Send Test Email</h3>
          <form onSubmit={handleTest} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Your Name:</label>
              <input
                type="text"
                value={testName}
                onChange={(e) => setTestName(e.target.value)}
                placeholder="Enter your name"
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Your Email:</label>
              <input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="your.email@example.com"
                style={styles.input}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.submitButton,
                ...(loading ? styles.buttonDisabled : {}),
              }}
            >
              {loading ? 'Sending...' : 'Send Test Email'}
            </button>
          </form>
        </div>

        {result && (
          <div
            style={{
              ...styles.result,
              ...(result.type === 'success'
                ? styles.successResult
                : result.type === 'error'
                ? styles.errorResult
                : styles.infoResult),
            }}
          >
            {result.message}
          </div>
        )}

        <div style={styles.instructions}>
          <h3>📝 Instructions:</h3>
          <ol>
            <li>
              Make sure you've updated <code>.env</code> with your EmailJS
              credentials
            </li>
            <li>Click "Check .env Configuration" to verify settings</li>
            <li>Enter your name and email address</li>
            <li>Click "Send Test Email"</li>
            <li>Check your inbox (and spam folder) for the approval email</li>
          </ol>

          <p style={styles.note}>
            <strong>Note:</strong> If you haven't set up your EmailJS account
            yet, follow the guide in <code>EMAILJS_QUICK_START.md</code>
          </p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    padding: '20px',
    backgroundColor: '#f5f5f5',
  } as React.CSSProperties,
  card: {
    maxWidth: '800px',
    margin: '0 auto',
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '40px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  } as React.CSSProperties,
  title: {
    fontSize: '32px',
    marginBottom: '8px',
    color: '#1a202c',
  } as React.CSSProperties,
  subtitle: {
    fontSize: '16px',
    color: '#718096',
    marginBottom: '40px',
  } as React.CSSProperties,
  section: {
    marginBottom: '30px',
    paddingBottom: '30px',
    borderBottom: '1px solid #e2e8f0',
  } as React.CSSProperties,
  checkButton: {
    padding: '12px 24px',
    backgroundColor: '#0066cc',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    marginBottom: '20px',
  } as React.CSSProperties,
  configInfo: {
    backgroundColor: '#f7fafc',
    padding: '15px',
    borderRadius: '6px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  } as React.CSSProperties,
  code: {
    backgroundColor: '#2d3748',
    color: '#68d391',
    padding: '8px 12px',
    borderRadius: '4px',
    fontFamily: 'monospace',
    fontSize: '13px',
    display: 'block',
  } as React.CSSProperties,
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  } as React.CSSProperties,
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  } as React.CSSProperties,
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#2d3748',
  } as React.CSSProperties,
  input: {
    padding: '12px',
    fontSize: '14px',
    border: '1px solid #cbd5e0',
    borderRadius: '6px',
    outline: 'none',
  } as React.CSSProperties,
  submitButton: {
    padding: '14px 24px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  } as React.CSSProperties,
  buttonDisabled: {
    backgroundColor: '#a0aec0',
    cursor: 'not-allowed',
  } as React.CSSProperties,
  result: {
    padding: '15px',
    borderRadius: '6px',
    marginTop: '20px',
    fontSize: '14px',
  } as React.CSSProperties,
  successResult: {
    backgroundColor: '#d4edda',
    color: '#155724',
    border: '1px solid #c3e6cb',
  } as React.CSSProperties,
  errorResult: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    border: '1px solid #f5c6cb',
  } as React.CSSProperties,
  infoResult: {
    backgroundColor: '#d1ecf1',
    color: '#0c5460',
    border: '1px solid #bee5eb',
  } as React.CSSProperties,
  instructions: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#e7f3ff',
    borderRadius: '6px',
  } as React.CSSProperties,
  note: {
    marginTop: '15px',
    padding: '10px',
    backgroundColor: '#fff3cd',
    borderLeft: '4px solid #ffc107',
    fontSize: '14px',
  } as React.CSSProperties,
};

export default EmailJsTest;
