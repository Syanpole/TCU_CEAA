import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient, ProfileImageResponse } from '../services/authService';
import ImageCropper from './ImageCropper';
import DefaultAvatar from './DefaultAvatar';
import './ProfileSettings.css';

// Declare VANTA global variable for TypeScript
declare global {
  interface Window {
    VANTA?: any;
    THREE?: any;
  }
}

interface ProfileUpdateData {
  first_name: string;
  last_name: string;
  email: string;
  username: string;
  student_id?: string;
  current_password?: string;
  new_password?: string;
  confirm_password?: string;
}

interface ProfileSettingsProps {
  onViewChange: (view: string) => void;
}

const ProfileSettings: React.FC<ProfileSettingsProps> = ({ onViewChange }) => {
  // Dynamically load Vanta and THREE scripts if missing
  useEffect(() => {
    const loadScript = (src: string) => {
      return new Promise<void>((resolve, reject) => {
        if (document.querySelector(`script[src='${src}']`)) {
          resolve();
          return;
        }
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        script.onload = () => resolve();
        script.onerror = () => reject();
        document.body.appendChild(script);
      });
    };
    Promise.all([
      loadScript('/three.r134.min.js'),
      loadScript('/vanta.net.min.js'),
    ]).catch(() => {
      console.warn('Vanta or THREE script failed to load');
    });
  }, []);
  const { user, refreshUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const vantaRef = useRef<HTMLDivElement>(null);
  const vantaEffect = useRef<any>(null);
  
  // Theme state - sync with StudentDashboard theme
  const [darkMode, setDarkMode] = useState(false);
  
  const [formData, setFormData] = useState<ProfileUpdateData>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    username: user?.username || '',
    student_id: user?.student_id || '',
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  const [profileImage, setProfileImage] = useState<string | null>(user?.profile_image_url || null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [cropImageSrc, setCropImageSrc] = useState<string | null>(null);
  const [showCropper, setShowCropper] = useState(false);
  const [croppedImageBlob, setCroppedImageBlob] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showPasswordSection, setShowPasswordSection] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Enhanced smooth theme toggle function
  const toggleTheme = () => {
    // Add a transitioning class for extra smooth effects
    const container = document.querySelector('.profile-settings-container');
    if (container) {
      container.classList.add('theme-transitioning');
      
      // Remove the transitioning class after animation completes
      setTimeout(() => {
        container.classList.remove('theme-transitioning');
      }, 600); // Match CSS transition duration
    }
    
    setDarkMode(!darkMode);
    // Save preference to localStorage
    localStorage.setItem('studentDashboardTheme', !darkMode ? 'dark' : 'light');
  };

  // Load saved theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('studentDashboardTheme');
    if (savedTheme === 'dark') {
      setDarkMode(true);
    } else {
      setDarkMode(false); // Explicitly set to false for light mode
    }
  }, []);

  // Initialize Vanta.js background effect
  useEffect(() => {
    const initVanta = () => {
      if (window.VANTA && window.THREE && vantaRef.current) {
        if (vantaEffect.current) {
          try {
            vantaEffect.current.destroy();
          } catch (error) {
            console.warn('Error destroying previous Vanta effect:', error);
          }
          vantaEffect.current = null;
        }
        setTimeout(() => {
          if (vantaRef.current && window.VANTA && window.THREE) {
            try {
              console.log('Initializing Vanta NET background...');
              vantaEffect.current = window.VANTA.NET({
                el: vantaRef.current,
                mouseControls: true,
                touchControls: true,
                gyroControls: false,
                minHeight: 200.00,
                minWidth: 200.00,
                scale: 1.00,
                scaleMobile: 1.00,
                color: darkMode ? 0xff4444 : 0xf20000,
                backgroundColor: darkMode ? 0x1a1a1a : 0xffffff,
                points: 10.00,
                maxDistance: 20.00,
                spacing: 15.00,
                showDots: true
              });
            } catch (error) {
              console.warn('Error initializing Vanta effect:', error);
            }
          }
        }, 200);
      } else {
        console.log('VANTA or THREE not loaded yet');
      }
    };
    const timer = setTimeout(initVanta, 400);
    return () => {
      clearTimeout(timer);
      if (vantaEffect.current) {
        try {
          vantaEffect.current.destroy();
        } catch (error) {
          console.warn('Error destroying Vanta effect on cleanup:', error);
        }
      }
    };
  }, [darkMode]);

  // Cleanup effect on unmount
  useEffect(() => {
    return () => {
      if (vantaEffect.current) {
        vantaEffect.current.destroy();
      }
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setMessage({ type: 'error', text: 'Image size must be less than 5MB' });
        return;
      }
      
      if (!file.type.startsWith('image/')) {
        setMessage({ type: 'error', text: 'Please select a valid image file (JPG, PNG, GIF, WebP)' });
        return;
      }
      
      // Create preview for cropper
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageUrl = e.target?.result as string;
        setCropImageSrc(imageUrl);
        setShowCropper(true);
      };
      reader.readAsDataURL(file);
      setMessage(null);
    }
  };

  const handleCropComplete = (croppedBlob: Blob) => {
    setCroppedImageBlob(croppedBlob);
    
    // Create preview URL for the cropped image
    const previewUrl = URL.createObjectURL(croppedBlob);
    setProfileImage(previewUrl);
    
    // Create file from blob for upload
    const croppedFile = new File([croppedBlob], 'profile-image.jpg', { type: 'image/jpeg' });
    setSelectedFile(croppedFile);
    
    setShowCropper(false);
    setCropImageSrc(null);
  };

  const handleCropCancel = () => {
    setShowCropper(false);
    setCropImageSrc(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleImageClick = () => {
    fileInputRef.current?.click();
  };

  const removeImage = () => {
    // If there was an original profile image, we need to call delete endpoint
    if (user?.profile_image_url && !selectedFile) {
      handleRemoveExistingImage();
      return;
    }
    
    // Clear local state
    setProfileImage(user?.profile_image_url || null);
    setSelectedFile(null);
    setCroppedImageBlob(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveExistingImage = async () => {
    try {
      setLoading(true);
      await apiClient.delete('/auth/profile/image/');
      setProfileImage(null);
      
      // Refresh user data to update profile image in the context
      await refreshUser();
      
      setMessage({ type: 'success', text: 'Profile image removed successfully!' });
    } catch (error) {
      console.error('Error removing image:', error);
      setMessage({ type: 'error', text: 'Failed to remove profile image. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const validateForm = (): boolean => {
    if (!formData.first_name.trim() || !formData.last_name.trim()) {
      setMessage({ type: 'error', text: 'First name and last name are required' });
      return false;
    }

    if (!formData.email.trim()) {
      setMessage({ type: 'error', text: 'Email is required' });
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' });
      return false;
    }

    if (!formData.username.trim()) {
      setMessage({ type: 'error', text: 'Username is required' });
      return false;
    }

    if (showPasswordSection) {
      if (!formData.current_password) {
        setMessage({ type: 'error', text: 'Current password is required to change password' });
        return false;
      }

      if (formData.new_password && formData.new_password.length < 6) {
        setMessage({ type: 'error', text: 'New password must be at least 6 characters long' });
        return false;
      }

      if (formData.new_password !== formData.confirm_password) {
        setMessage({ type: 'error', text: 'New passwords do not match' });
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const updateData: any = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        username: formData.username,
      };

      if (user?.role === 'student' && formData.student_id) {
        updateData.student_id = formData.student_id;
      }

      if (showPasswordSection && formData.new_password) {
        updateData.current_password = formData.current_password;
        updateData.new_password = formData.new_password;
      }

      // Update profile information
      await apiClient.put('/auth/profile/', updateData);

      // Upload profile image if selected
      if (selectedFile) {
        const imageFormData = new FormData();
        imageFormData.append('profile_image', selectedFile);
        const imageResponse = await apiClient.post<ProfileImageResponse>('/auth/profile/image/', imageFormData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        // Update local profile image URL
        if (imageResponse.data.profile_image) {
          setProfileImage(imageResponse.data.profile_image);
        }
        
        // Refresh user data to update profile image in the context
        await refreshUser();
      }

      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      
      // Reset password fields
      if (showPasswordSection) {
        setFormData(prev => ({
          ...prev,
          current_password: '',
          new_password: '',
          confirm_password: '',
        }));
        setShowPasswordSection(false);
      }

      // Clear selected file after successful upload
      setSelectedFile(null);
      setCroppedImageBlob(null);
      
    } catch (error: any) {
      console.error('Profile update error:', error);
      if (error.response?.data) {
        const errorData = error.response.data;
        if (typeof errorData === 'string') {
          setMessage({ type: 'error', text: errorData });
        } else if (errorData.detail) {
          setMessage({ type: 'error', text: errorData.detail });
        } else {
          const errorMessages = Object.entries(errorData)
            .map(([field, errors]: [string, any]) => {
              if (Array.isArray(errors)) {
                return `${field}: ${errors.join(', ')}`;
              }
              return `${field}: ${errors}`;
            });
          setMessage({ type: 'error', text: errorMessages.join('. ') });
        }
      } else {
        setMessage({ type: 'error', text: 'Failed to update profile. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  if (!user) {
    return (
      <div className={`profile-settings-container ${darkMode ? 'dark-theme' : ''}`}>
        <div className="no-user-message">
          <h2>Please log in to access your profile</h2>
        </div>
      </div>
    );
  }

  return (
    <div className={`profile-settings-container ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Vanta.js animated background - ensure first child for layering */}
      <div
        ref={vantaRef}
        className={`vanta-background${darkMode ? ' dark-theme' : ' light-theme'}`}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          zIndex: -1,
          pointerEvents: 'none',
        }}
      />

      {showCropper && cropImageSrc && (
        <ImageCropper
          imageSrc={cropImageSrc}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
        />
      )}

      <div className="profile-settings-card">
        <div className="profile-header">
          <button
            type="button"
            className="back-button"
            onClick={() => onViewChange('dashboard')}
            aria-label="Go back"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="back-icon"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              width="20"
              height="20"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <h1>Profile Settings</h1>
        </div>
        <p
          style={{
            textAlign: 'center',
            marginTop: '0.5rem',
            marginBottom: '1rem',
            color: darkMode ? '#f5f5f5' : '#b22222', // light gray for dark, dark red for light
            width: '100%',
            fontWeight: 500,
            fontSize: '1.05rem',
            textShadow: darkMode ? '0 1px 4px #000' : '0 1px 2px #fff'
          }}
        >
          Update your account information and preferences
        </p>

        <form onSubmit={handleSubmit} className="profile-form">
          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          {/* Profile Image Section */}
          <div className="profile-image-section">
            <h3>Profile Photo</h3>
            <div className="image-upload-container">
              <div className="profile-image-wrapper" onClick={handleImageClick}>
                {profileImage ? (
                  <img src={profileImage} alt="Profile" className="profile-image" />
                ) : (
                  <div className="profile-image-placeholder">
                    <DefaultAvatar 
                      firstName={formData.first_name}
                      lastName={formData.last_name}
                      size={120}
                      className="profile-image-default-avatar"
                    />
                    <div className="upload-prompt">
                      <span>Click to upload</span>
                    </div>
                  </div>
                )}
                <div className="image-overlay">
                  <span>Change Image</span>
                </div>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageUpload}
                accept="image/*"
                className="hidden-file-input"
              />
              {profileImage && (
                <button
                  type="button"
                  onClick={removeImage}
                  className="remove-image-button"
                >
                  Remove Image
                </button>
              )}
              <p className="image-help-text">
                Max 5MB. Supports JPG, PNG, GIF, WebP.
              </p>
            </div>
          </div>

          {/* Personal Information */}
          <div className="form-section">
            <h3>Personal Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="First name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="last_name">Last Name</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Last name"
                />
              </div>
            </div>
          </div>

          {/* Account Information */}
          <div className="form-section">
            <h3>Account Information</h3>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Username"
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Email address"
              />
            </div>
            {user.role === 'student' && (
              <div className="form-group">
                <label htmlFor="student_id">Student ID</label>
                <input
                  type="text"
                  id="student_id"
                  name="student_id"
                  value={formData.student_id}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Student ID"
                />
              </div>
            )}
            <div className="role-display">
              <label>Role</label>
              <div className="role-badge">
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </div>
            </div>
          </div>

          {/* Password Section */}
          <div className="form-section">
            <div className="password-section-header">
              <h3>Password</h3>
              <button
                type="button"
                onClick={() => setShowPasswordSection(!showPasswordSection)}
                className="toggle-password-section"
              >
                {showPasswordSection ? 'Cancel' : 'Change Password'}
              </button>
            </div>

            {showPasswordSection && (
              <div className="password-fields">
                <div className="form-group">
                  <label htmlFor="current_password">Current Password</label>
                  <div className="input-wrapper">
                    <input
                      type={showPasswords.current ? "text" : "password"}
                      id="current_password"
                      name="current_password"
                      value={formData.current_password}
                      onChange={handleInputChange}
                      required
                      className="form-input"
                      placeholder="Current password"
                    />
                    <button
                      type="button"
                      className="password-toggle-button"
                      onClick={() => togglePasswordVisibility('current')}
                      aria-label={showPasswords.current ? "Hide password" : "Show password"}
                    >
                      {showPasswords.current ? 'Hide' : 'Show'}
                    </button>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="new_password">New Password</label>
                    <div className="input-wrapper">
                      <input
                        type={showPasswords.new ? "text" : "password"}
                        id="new_password"
                        name="new_password"
                        value={formData.new_password}
                        onChange={handleInputChange}
                        required
                        className="form-input"
                        placeholder="New password"
                        minLength={6}
                      />
                      <button
                        type="button"
                        className="password-toggle-button"
                        onClick={() => togglePasswordVisibility('new')}
                        aria-label={showPasswords.new ? "Hide password" : "Show password"}
                      >
                        {showPasswords.new ? 'Hide' : 'Show'}
                      </button>
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="confirm_password">Confirm Password</label>
                    <div className="input-wrapper">
                      <input
                        type={showPasswords.confirm ? "text" : "password"}
                        id="confirm_password"
                        name="confirm_password"
                        value={formData.confirm_password}
                        onChange={handleInputChange}
                        required
                        className="form-input"
                        placeholder="Confirm password"
                        minLength={6}
                      />
                      <button
                        type="button"
                        className="password-toggle-button"
                        onClick={() => togglePasswordVisibility('confirm')}
                        aria-label={showPasswords.confirm ? "Hide password" : "Show password"}
                      >
                        {showPasswords.confirm ? 'Hide' : 'Show'}
                      </button>
                    </div>
                  </div>
                </div>
                <p className="password-help-text">
                  Minimum 6 characters required
                </p>
              </div>
            )}
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="save-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileSettings;