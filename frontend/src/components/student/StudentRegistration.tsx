import React, { useState, FormEvent } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiClient } from '../../services/authService';
import './StudentRegistration.css';

interface StudentData {
  first_name: string;
  last_name: string;
  email: string;
  student_id: string;
  contact_number: string;
  address: string;
  course: string;
  year_level: string;
  password: string;
  confirm_password: string;
}

interface FormErrors {
  [key: string]: string;
}

const StudentRegistration: React.FC = () => {
  const [formData, setFormData] = useState<StudentData>({
    first_name: '',
    last_name: '',
    email: '',
    student_id: '',
    contact_number: '',
    address: '',
    course: '',
    year_level: '',
    password: '',
    confirm_password: ''
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Required field validations
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!formData.student_id.trim()) {
      newErrors.student_id = 'Student ID is required';
    }
    if (!formData.contact_number.trim()) {
      newErrors.contact_number = 'Contact number is required';
    } else if (!/^\d{11}$/.test(formData.contact_number.replace(/[^0-9]/g, ''))) {
      newErrors.contact_number = 'Please enter a valid 11-digit phone number';
    }
    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }
    if (!formData.course.trim()) {
      newErrors.course = 'Course is required';
    }
    if (!formData.year_level) {
      newErrors.year_level = 'Year level is required';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters long';
    }
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const registrationData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        student_id: formData.student_id,
        contact_number: formData.contact_number,
        address: formData.address,
        course: formData.course,
        year_level: formData.year_level,
        password: formData.password
      };

      const response = await apiClient.post('/auth/register/', registrationData);

      if (response.status === 201) {
        setSuccess(true);
        setFormData({
          first_name: '',
          last_name: '',
          email: '',
          student_id: '',
          contact_number: '',
          address: '',
          course: '',
          year_level: '',
          password: '',
          confirm_password: ''
        });
      }
    } catch (error: any) {
      if (error.response && error.response.data) {
        const serverErrors: FormErrors = {};
        Object.keys(error.response.data).forEach(key => {
          if (Array.isArray(error.response.data[key])) {
            serverErrors[key] = error.response.data[key][0];
          } else {
            serverErrors[key] = error.response.data[key];
          }
        });
        setErrors(serverErrors);
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const courses = [
    'Bachelor of Science in Information Technology',
    'Bachelor of Science in Computer Science',
    'Bachelor of Science in Information Systems',
    'Bachelor of Science in Computer Engineering',
    'Bachelor of Science in Business Administration',
    'Bachelor of Science in Accountancy',
    'Bachelor of Science in Nursing',
    'Bachelor of Science in Psychology',
    'Bachelor of Arts in Communication',
    'Bachelor of Elementary Education',
    'Bachelor of Secondary Education'
  ];

  if (success) {
    return (
      <div className="registration-container">
        <div className="registration-card">
          <div className="success-message">
            <div className="success-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="60" height="60">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2>Registration Successful!</h2>
            <p>Your account has been created successfully. Please check your email for verification instructions.</p>
            <button 
              className="login-redirect-btn"
              onClick={() => window.location.href = '/login'}
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="registration-container">
      <div className="registration-card">
        <div className="registration-header">
          <h1>Student Registration</h1>
          <p>Join the TCU-CEAA Educational Assistance Program</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          {errors.general && (
            <div className="error-alert">
              {errors.general}
            </div>
          )}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name *</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className={errors.first_name ? 'error' : ''}
                placeholder="Enter your first name"
                disabled={loading}
              />
              {errors.first_name && <span className="error-text">{errors.first_name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name *</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className={errors.last_name ? 'error' : ''}
                placeholder="Enter your last name"
                disabled={loading}
              />
              {errors.last_name && <span className="error-text">{errors.last_name}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter your email address"
                disabled={loading}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="student_id">Student ID *</label>
              <input
                type="text"
                id="student_id"
                name="student_id"
                value={formData.student_id}
                onChange={handleInputChange}
                className={errors.student_id ? 'error' : ''}
                placeholder="Enter your student ID"
                disabled={loading}
              />
              {errors.student_id && <span className="error-text">{errors.student_id}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="contact_number">Contact Number *</label>
              <input
                type="tel"
                id="contact_number"
                name="contact_number"
                value={formData.contact_number}
                onChange={handleInputChange}
                className={errors.contact_number ? 'error' : ''}
                placeholder="09XX XXX XXXX"
                disabled={loading}
              />
              {errors.contact_number && <span className="error-text">{errors.contact_number}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="year_level">Year Level *</label>
              <select
                id="year_level"
                name="year_level"
                value={formData.year_level}
                onChange={handleInputChange}
                className={errors.year_level ? 'error' : ''}
                disabled={loading}
              >
                <option value="">Select year level</option>
                <option value="1">1st Year</option>
                <option value="2">2nd Year</option>
                <option value="3">3rd Year</option>
                <option value="4">4th Year</option>
                <option value="5">5th Year</option>
              </select>
              {errors.year_level && <span className="error-text">{errors.year_level}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="course">Course/Program *</label>
            <select
              id="course"
              name="course"
              value={formData.course}
              onChange={handleInputChange}
              className={errors.course ? 'error' : ''}
              disabled={loading}
            >
              <option value="">Select your course</option>
              {courses.map((course, index) => (
                <option key={index} value={course}>
                  {course}
                </option>
              ))}
            </select>
            {errors.course && <span className="error-text">{errors.course}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="address">Complete Address *</label>
            <textarea
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              className={errors.address ? 'error' : ''}
              placeholder="Enter your complete address"
              rows={3}
              disabled={loading}
            />
            {errors.address && <span className="error-text">{errors.address}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">Password *</label>
              <div className="password-field">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={errors.password ? 'error' : ''}
                  placeholder="Enter your password"
                  disabled={loading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={loading}
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm Password *</label>
              <div className="password-field">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirm_password"
                  name="confirm_password"
                  value={formData.confirm_password}
                  onChange={handleInputChange}
                  className={errors.confirm_password ? 'error' : ''}
                  placeholder="Confirm your password"
                  disabled={loading}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  disabled={loading}
                >
                  {showConfirmPassword ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
              {errors.confirm_password && <span className="error-text">{errors.confirm_password}</span>}
            </div>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="register-btn"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading-spinner"></div>
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </div>

          <div className="form-footer">
            <p>
              Already have an account?{' '}
              <a href="/login" className="login-link">
                Sign in here
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StudentRegistration;