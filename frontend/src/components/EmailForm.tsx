import React, { useState } from 'react';
import { sendApprovalEmail } from '../services/email/emailService';

interface FormData {
  studentName: string;
  studentEmail: string;
}

interface FormErrors {
  studentName?: string;
  studentEmail?: string;
}

const EmailForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    studentName: '',
    studentEmail: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.studentName.trim()) {
      newErrors.studentName = 'Student name is required';
    }

    if (!formData.studentEmail.trim()) {
      newErrors.studentEmail = 'Student email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.studentEmail)) {
      newErrors.studentEmail = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear messages
    setSuccessMessage('');
    setErrorMessage('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      const result = await sendApprovalEmail(
        formData.studentName,
        formData.studentEmail
      );

      if (result.success) {
        setSuccessMessage(
          `Approval email sent successfully to ${formData.studentEmail}!`
        );
        // Reset form
        setFormData({
          studentName: '',
          studentEmail: '',
        });
      } else {
        setErrorMessage(result.message);
      }
    } catch (error) {
      setErrorMessage('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="email-form-container" style={styles.container}>
      <div className="email-form-card" style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.title}>TCU-CEAA Approval Email</h2>
          <p style={styles.subtitle}>
            Send approval notification to approved students
          </p>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label htmlFor="studentName" style={styles.label}>
              Student Name <span style={styles.required}>*</span>
            </label>
            <input
              type="text"
              id="studentName"
              name="studentName"
              value={formData.studentName}
              onChange={handleChange}
              placeholder="Enter student's full name"
              style={{
                ...styles.input,
                ...(errors.studentName ? styles.inputError : {}),
              }}
            />
            {errors.studentName && (
              <span style={styles.errorText}>{errors.studentName}</span>
            )}
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="studentEmail" style={styles.label}>
              Student Email <span style={styles.required}>*</span>
            </label>
            <input
              type="email"
              id="studentEmail"
              name="studentEmail"
              value={formData.studentEmail}
              onChange={handleChange}
              placeholder="student@example.com"
              style={{
                ...styles.input,
                ...(errors.studentEmail ? styles.inputError : {}),
              }}
            />
            {errors.studentEmail && (
              <span style={styles.errorText}>{errors.studentEmail}</span>
            )}
          </div>

          {successMessage && (
            <div style={styles.successMessage}>
              <div style={styles.successIcon}>✓</div>
              <div>
                <strong>Success!</strong>
                <p style={styles.messageText}>{successMessage}</p>
              </div>
            </div>
          )}

          {errorMessage && (
            <div style={styles.errorMessage}>
              <div style={styles.errorIcon}>✕</div>
              <div>
                <strong>Error!</strong>
                <p style={styles.messageText}>{errorMessage}</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? (
              <>
                <span style={styles.spinner}></span>
                Sending...
              </>
            ) : (
              'Send Approval Email'
            )}
          </button>
        </form>

        <div style={styles.infoBox}>
          <p style={styles.infoText}>
            📧 This will send the official TCU-CEAA approval notification to the
            student's email address.
          </p>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    backgroundColor: '#f5f5f5',
  } as React.CSSProperties,
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '40px',
    maxWidth: '600px',
    width: '100%',
  } as React.CSSProperties,
  header: {
    marginBottom: '30px',
    textAlign: 'center',
  } as React.CSSProperties,
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1a202c',
    marginBottom: '8px',
  } as React.CSSProperties,
  subtitle: {
    fontSize: '14px',
    color: '#718096',
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
    fontWeight: '500',
    color: '#2d3748',
  } as React.CSSProperties,
  required: {
    color: '#e53e3e',
  } as React.CSSProperties,
  input: {
    padding: '12px 16px',
    fontSize: '14px',
    border: '1px solid #cbd5e0',
    borderRadius: '8px',
    outline: 'none',
    transition: 'all 0.2s',
  } as React.CSSProperties,
  inputError: {
    borderColor: '#e53e3e',
  } as React.CSSProperties,
  errorText: {
    fontSize: '12px',
    color: '#e53e3e',
    marginTop: '4px',
  } as React.CSSProperties,
  successMessage: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '16px',
    backgroundColor: '#c6f6d5',
    border: '1px solid #48bb78',
    borderRadius: '8px',
    color: '#22543d',
  } as React.CSSProperties,
  successIcon: {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    backgroundColor: '#48bb78',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    flexShrink: 0,
  } as React.CSSProperties,
  errorMessage: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '12px',
    padding: '16px',
    backgroundColor: '#fed7d7',
    border: '1px solid #e53e3e',
    borderRadius: '8px',
    color: '#742a2a',
  } as React.CSSProperties,
  errorIcon: {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    backgroundColor: '#e53e3e',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    flexShrink: 0,
  } as React.CSSProperties,
  messageText: {
    margin: '4px 0 0 0',
    fontSize: '14px',
  } as React.CSSProperties,
  button: {
    padding: '14px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#3182ce',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
  } as React.CSSProperties,
  buttonDisabled: {
    backgroundColor: '#a0aec0',
    cursor: 'not-allowed',
  } as React.CSSProperties,
  spinner: {
    width: '16px',
    height: '16px',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderTop: '2px solid white',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  } as React.CSSProperties,
  infoBox: {
    marginTop: '20px',
    padding: '12px',
    backgroundColor: '#ebf8ff',
    border: '1px solid #90cdf4',
    borderRadius: '8px',
  } as React.CSSProperties,
  infoText: {
    fontSize: '13px',
    color: '#2c5282',
    margin: 0,
  } as React.CSSProperties,
};

// Add keyframe animation for spinner
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default EmailForm;
