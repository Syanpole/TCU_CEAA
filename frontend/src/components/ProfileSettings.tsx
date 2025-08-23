import React, { useState, useRef } from 'react';
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
      <div className="profile-settings-container">
        <div className="no-user-message">
          <h2>Please log in to access profile settings</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-settings-container">
      {showCropper && cropImageSrc && (
        <ImageCropper
          imageSrc={cropImageSrc}
          onCropComplete={handleCropComplete}
          onCancel={handleCropCancel}
        />
      )}
      
      <div className="profile-settings-card">
        <div className="profile-header">
          <h1>Profile Settings</h1>
          <p>Manage your account information and preferences</p>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          {message && (
            <div className={`message ${message.type}`}>
              <span className="message-icon">
                {message.type === 'success' ? (
                  <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                )}
              </span>
              {message.text}
            </div>
          )}

          {/* Profile Image Section */}
          <div className="profile-image-section">
            <h3>Profile Picture</h3>
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
                      <span className="image-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                          <path d="M12 9a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path d="M6 18.5a6 6 0 1112 0H6z" />
                        </svg>
                      </span>
                      <span>Click to upload photo</span>
                    </div>
                  </div>
                )}
                <div className="image-overlay">
                  <span>Change Photo</span>
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
                  Remove Photo
                </button>
              )}
              <p className="image-help-text">
                Recommended: Square image, max 5MB. Supports JPG, PNG, GIF, WebP.
              </p>
            </div>
          </div>

          {/* Personal Information */}
          <div className="form-section">
            <h3>Personal Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="first_name">First Name *</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Enter your first name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="last_name">Last Name *</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  placeholder="Enter your last name"
                />
              </div>
            </div>
          </div>

          {/* Account Information */}
          <div className="form-section">
            <h3>Account Information</h3>
            <div className="form-group">
              <label htmlFor="username">Username *</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your username"
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email Address *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="form-input"
                placeholder="Enter your email address"
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
                  placeholder="Enter your student ID"
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
                {showPasswordSection ? 'Cancel Password Change' : 'Change Password'}
              </button>
            </div>

            {showPasswordSection && (
              <div className="password-fields">
                <div className="form-group">
                  <label htmlFor="current_password">Current Password *</label>
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
                    />
                    <button
                      type="button"
                      className="password-toggle-button"
                      onClick={() => togglePasswordVisibility('current')}
                      aria-label={showPasswords.current ? "Hide password" : "Show password"}
                    >
                      {showPasswords.current ? (
                        // Eye open icon
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                          <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                      ) : (
                        // Eye closed icon
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="new_password">New Password *</label>
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
                      />
                      <button
                        type="button"
                        className="password-toggle-button"
                        onClick={() => togglePasswordVisibility('new')}
                        aria-label={showPasswords.new ? "Hide password" : "Show password"}
                      >
                        {showPasswords.new ? (
                          // Eye open icon
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                            <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                        ) : (
                          // Eye closed icon
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  <div className="form-group">
                    <label htmlFor="confirm_password">Confirm New Password *</label>
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
                      />
                      <button
                        type="button"
                        className="password-toggle-button"
                        onClick={() => togglePasswordVisibility('confirm')}
                        aria-label={showPasswords.confirm ? "Hide password" : "Show password"}
                      >
                        {showPasswords.confirm ? (
                          // Eye open icon
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2"/>
                            <path d="M2.45801 12.3051C2.31292 12.1136 2.31292 11.8864 2.45801 11.6949C4.41421 9.13734 8.02319 6 12 6C15.9768 6 19.5858 9.13734 21.542 11.6949C21.6871 11.8864 21.6871 12.1136 21.542 12.3051C19.5858 14.8627 15.9768 18 12 18C8.02319 18 4.41421 14.8627 2.45801 12.3051Z" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                        ) : (
                          // Eye closed icon
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6.87292 6.87292L17.1271 17.1271" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M12 5C8.02319 5 4.41421 8.13734 2.45801 10.6949C2.31292 10.8864 2.31292 11.1136 2.45801 11.3051C3.73228 12.8737 5.88258 15.0583 8.5 16.1547M12 19C15.9768 19 19.5858 15.8627 21.542 13.3051C21.6871 13.1136 21.6871 12.8864 21.542 12.6949C20.2677 11.1263 18.1174 8.94167 15.5 7.84533" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                            <path d="M9.87868 9.87868C9.33579 10.4216 9 11.1716 9 12C9 13.6569 10.3431 15 12 15C12.8284 15 13.5784 14.6642 14.1213 14.1213" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
                <p className="password-help-text">
                  Password must be at least 6 characters long
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
                  Saving Changes...
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