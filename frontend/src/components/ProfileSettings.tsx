import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiClient, ProfileImageResponse } from '../services/authService';
import ImageCropper from './ImageCropper';
import DefaultAvatar from './DefaultAvatar';
import './ProfileSettings.css';

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

const ProfileSettings: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Theme state - sync with StudentDashboard theme
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'personal' | 'account' | 'password'>('personal');
  
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

  // Utility function for consistent input styling
  const getInputStyle = () => ({
    backgroundColor: darkMode ? '#1e293b' : '#ffffff',
    color: darkMode ? '#f8fafc' : '#0f172a',
    border: `2px solid ${darkMode ? '#334155' : '#e2e8f0'}`,
    WebkitTextFillColor: darkMode ? '#f8fafc' : '#0f172a'
  });

  // Load saved theme preference and sync with StudentDashboard
  useEffect(() => {
    const loadTheme = () => {
      const savedTheme = localStorage.getItem('studentDashboardTheme');
      const isDark = savedTheme === 'dark';
      setDarkMode(isDark);
      
      // Debug log to verify theme loading
      console.log('ProfileSettings theme loaded:', isDark ? 'dark' : 'light');
    };

    // Load initial theme
    loadTheme();

    // Listen for localStorage changes (cross-tab)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'studentDashboardTheme') {
        const isDark = e.newValue === 'dark';
        setDarkMode(isDark);
        console.log('ProfileSettings theme changed via storage:', isDark ? 'dark' : 'light');
      }
    };

    // Listen for custom theme change events (same-tab)
    const handleThemeChange = (e: CustomEvent) => {
      setDarkMode(e.detail.darkMode);
      console.log('ProfileSettings theme changed via event:', e.detail.darkMode ? 'dark' : 'light');
    };

    // Periodic theme check as fallback
    const themeChecker = setInterval(() => {
      const currentTheme = localStorage.getItem('studentDashboardTheme');
      const shouldBeDark = currentTheme === 'dark';
      if (shouldBeDark !== darkMode) {
        setDarkMode(shouldBeDark);
        console.log('ProfileSettings theme synced via interval:', shouldBeDark ? 'dark' : 'light');
      }
    }, 500); // Check every 500ms for immediate response

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('themeChange', handleThemeChange as EventListener);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('themeChange', handleThemeChange as EventListener);
      clearInterval(themeChecker);
    };
  }, [darkMode]);

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
          <h2>Please log in to access profile settings</h2>
        </div>
      </div>
    );
  }

  return (
    <div className={`profile-settings-container ${darkMode ? 'dark-theme' : ''}`}>
      {showCropper && cropImageSrc && (
        <ImageCropper
          imageSrc={cropImageSrc}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
        />
      )}
      
      <div className="profile-settings-wrapper">
        <div className="profile-settings-title">
          <h1>Profile Settings</h1>
        </div>

        <div 
          className="profile-settings-card"
          style={{
            backgroundColor: darkMode ? '#1e293b' : '#ffffff',
            color: darkMode ? '#f8fafc' : '#0f172a'
          }}
        >
          {/* Profile Photo Section */}
          <div className="profile-photo-section">
            <h2>Profile Photo</h2>
            <p className="section-subtitle">Upload your profile picture</p>
            
            <div className="photo-upload-wrapper">
              <div className="profile-image-container" onClick={handleImageClick}>
                {profileImage ? (
                  <img src={profileImage} alt="Profile" className="profile-image" />
                ) : (
                  <div className="profile-image-placeholder">
                    <DefaultAvatar 
                      firstName={formData.first_name}
                      lastName={formData.last_name}
                      size={100}
                      className="profile-image-default-avatar"
                    />
                  </div>
                )}
                <div className="image-overlay">
                  <span>Change Photo</span>
                </div>
              </div>
              
              <div className="photo-actions">
                <button
                  type="button"
                  onClick={handleImageClick}
                  className="upload-photo-button"
                >
                  Upload Photo
                </button>
                <p className="photo-help-text">JPG, PNG or GIF. Max 5MB.</p>
              </div>
            </div>
            
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              accept="image/*"
              className="hidden-file-input"
            />
          </div>

          {/* Tab Navigation */}
          <div className="tab-navigation">
            <button
              className={`tab-button ${activeTab === 'personal' ? 'active' : ''}`}
              onClick={() => setActiveTab('personal')}
              type="button"
            >
              Personal Info
            </button>
            <button
              className={`tab-button ${activeTab === 'account' ? 'active' : ''}`}
              onClick={() => setActiveTab('account')}
              type="button"
            >
              Account Info
            </button>
            <button
              className={`tab-button ${activeTab === 'password' ? 'active' : ''}`}
              onClick={() => setActiveTab('password')}
              type="button"
            >
              Password
            </button>
          </div>

          <form onSubmit={handleSubmit} className="profile-form">
            {message && (
              <div className={`message ${message.type}`}>
                {message.text}
              </div>
            )}

            {/* Personal Info Tab */}
            {activeTab === 'personal' && (
              <div className="tab-content">
                <div className="tab-content-header">
                  <h3>Personal Information</h3>
                  <p className="tab-subtitle">Update your personal details</p>
                </div>

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
                      placeholder="Enter your first name"
                      style={getInputStyle()}
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
                      placeholder="Enter your last name"
                      style={getInputStyle()}
                    />
                  </div>
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
                      placeholder="Enter your student ID"
                      style={getInputStyle()}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Account Info Tab */}
            {activeTab === 'account' && (
              <div className="tab-content">
                <div className="tab-content-header">
                  <h3>Account Information</h3>
                  <p className="tab-subtitle">Manage your account details</p>
                </div>

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
                    placeholder="Enter your username"
                    style={getInputStyle()}
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
                    placeholder="Enter your email address"
                    style={getInputStyle()}
                  />
                </div>

                <div className="role-display">
                  <label>Role</label>
                  <div className="role-badge">
                    {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                  </div>
                </div>
              </div>
            )}

            {/* Password Tab */}
            {activeTab === 'password' && (
              <div className="tab-content">
                <div className="tab-content-header">
                  <h3>Change Password</h3>
                  <p className="tab-subtitle">Update your password</p>
                </div>

                {!showPasswordSection ? (
                  <button
                    type="button"
                    onClick={() => setShowPasswordSection(true)}
                    className="change-password-button"
                  >
                    Change Password
                  </button>
                ) : (
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
                          placeholder="Enter your current password"
                          style={getInputStyle()}
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
                            placeholder="Enter new password"
                            minLength={6}
                            style={getInputStyle()}
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
                        <label htmlFor="confirm_password">Confirm New Password</label>
                        <div className="input-wrapper">
                          <input
                            type={showPasswords.confirm ? "text" : "password"}
                            id="confirm_password"
                            name="confirm_password"
                            value={formData.confirm_password}
                            onChange={handleInputChange}
                            required
                            className="form-input"
                            placeholder="Confirm new password"
                            minLength={6}
                            style={getInputStyle()}
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
                      Password must be at least 6 characters long
                    </p>

                    <button
                      type="button"
                      onClick={() => {
                        setShowPasswordSection(false);
                        setFormData(prev => ({
                          ...prev,
                          current_password: '',
                          new_password: '',
                          confirm_password: '',
                        }));
                      }}
                      className="cancel-password-button"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            )}

            <div className="form-actions">
              <button
                type="submit"
                className="save-button"
                disabled={loading}
              >
                {loading ? 'Saving Changes...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;