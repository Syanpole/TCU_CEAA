import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/authService';
import './FullApplicationForm.css';

interface FullApplicationFormProps {
  applicantType: 'new' | 'renewing';
  onComplete: (data: { school_year: string; semester: string }) => void;
  onCancel: () => void;
}

interface ApplicationData {
  // Application Details
  facebook_link: string;
  application_type: string;
  scholarship_type: string;
  school_year: string;
  semester: string;
  applying_for_merit: string;
  
  // Personal Information
  first_name: string;
  middle_name: string;
  last_name: string;
  house_no: string;
  street: string;
  zip_code: string;
  barangay: string;
  district: string;
  mobile_no: string;
  other_contact: string;
  email: string;
  date_of_birth: string;
  age: string;
  citizenship: string;
  sex: string;
  marital_status: string;
  religion: string;
  place_of_birth: string;
  years_of_residency: string;
  
  // School Information
  course_name: string;
  ladderized: string;
  year_level: string;
  swa_input: string;
  units_enrolled: string;
  course_duration: string;
  school_name: string;
  school_address: string;
  graduating_this_term: string;
  semesters_to_graduate: string;
  with_honors: string;
  transferee: string;
  shiftee: string;
  status: string;
  
  // Educational Background
  shs_attended: string;
  shs_type: string;
  shs_address: string;
  shs_years: string;
  shs_honors: string;
  jhs_attended: string;
  jhs_type: string;
  jhs_address: string;
  jhs_years: string;
  jhs_honors: string;
  elem_attended: string;
  elem_type: string;
  elem_address: string;
  elem_years: string;
  elem_honors: string;
  
  // Parents Information
  father_name: string;
  father_address: string;
  father_contact: string;
  father_occupation: string;
  father_place_of_work: string;
  father_education: string;
  father_deceased: boolean;
  mother_name: string;
  mother_address: string;
  mother_contact: string;
  mother_occupation: string;
  mother_place_of_work: string;
  mother_education: string;
  mother_deceased: boolean;
}

const FullApplicationForm: React.FC<FullApplicationFormProps> = ({ applicantType, onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [showReview, setShowReview] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [draftFadingOut, setDraftFadingOut] = useState(false);
  const [checkingExisting, setCheckingExisting] = useState(true);
  const [hasExistingApplication, setHasExistingApplication] = useState(false);
  const totalSteps = 5;

  const [formData, setFormData] = useState<ApplicationData>({
    facebook_link: '',
    application_type: applicantType === 'renewing' ? 'RENEW' : 'NEW',
    scholarship_type: 'TCU-CEAA',
    school_year: '',
    semester: '',
    applying_for_merit: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    house_no: '',
    street: '',
    zip_code: '',
    barangay: '',
    district: '',
    mobile_no: '',
    other_contact: 'N/A',
    email: '',
    date_of_birth: '',
    age: '',
    citizenship: 'Filipino',
    sex: '',
    marital_status: '',
    religion: '',
    place_of_birth: 'Taguig City',
    years_of_residency: '',
    course_name: '',
    ladderized: 'NO',
    year_level: '',
    swa_input: '',
    units_enrolled: '',
    course_duration: '',
    school_name: 'TAGUIG CITY UNIVERSITY (TCU)',
    school_address: 'Gen. Santos Ave., Central Bicutan, Taguig City',
    graduating_this_term: '',
    semesters_to_graduate: '',
    with_honors: '',
    transferee: '',
    shiftee: '',
    status: '',
    shs_attended: '',
    shs_type: '',
    shs_address: '',
    shs_years: '',
    shs_honors: '',
    jhs_attended: '',
    jhs_type: '',
    jhs_address: '',
    jhs_years: '',
    jhs_honors: '',
    elem_attended: '',
    elem_type: '',
    elem_address: '',
    elem_years: '',
    elem_honors: '',
    father_name: '',
    father_address: '',
    father_contact: '',
    father_occupation: '',
    father_place_of_work: '',
    father_education: '',
    father_deceased: false,
    mother_name: '',
    mother_address: '',
    mother_contact: '',
    mother_occupation: '',
    mother_place_of_work: '',
    mother_education: '',
    mother_deceased: false,
  });

  // Check for existing application on mount
  useEffect(() => {
    const checkExistingApplication = async () => {
      try {
        setCheckingExisting(true);
        const response = await apiClient.get('/full-application/');
        const applications = Array.isArray(response.data) ? response.data : [];
        
        if (applications.length > 0) {
          // User already has a submitted application
          const latestApp = applications[0];
          console.log('⚠️ Found existing application:', latestApp);
          setHasExistingApplication(true);
          
          // Notify parent that user already has an application
          setTimeout(() => {
            alert('You have already submitted an application. You can only submit one application at a time.');
            onCancel();
          }, 500);
        } else {
          setHasExistingApplication(false);
        }
      } catch (error: any) {
        console.error('Error checking existing application:', error);
        // If error is 404 or empty, user has no applications (which is good)
        if (error.response?.status === 404 || error.response?.status === 400) {
          setHasExistingApplication(false);
        }
      } finally {
        setCheckingExisting(false);
      }
    };

    checkExistingApplication();
  }, [onCancel]);

  // Load saved draft from localStorage on component mount
  useEffect(() => {
    // Don't load draft if user already has a submitted application
    if (hasExistingApplication || checkingExisting) {
      return;
    }

    const savedDraft = localStorage.getItem('fullApplicationDraft');
    if (savedDraft) {
      try {
        const parsedDraft = JSON.parse(savedDraft);
        // Only load if it's for the same applicant type
        if (parsedDraft.application_type === (applicantType === 'renewing' ? 'RENEW' : 'NEW')) {
          setFormData(parsedDraft);
          setDraftLoaded(true);
          console.log('✅ Draft loaded from localStorage');
        }
      } catch (error) {
        console.error('Error loading saved draft:', error);
      }
    }
  }, [applicantType, hasExistingApplication, checkingExisting]);

  // Auto-hide draft notification after 45 seconds
  useEffect(() => {
    if (draftLoaded) {
      const fadeTimer = setTimeout(() => {
        setDraftFadingOut(true); // Start fade-out animation
        
        // Wait for animation to complete before removing
        setTimeout(() => {
          setDraftLoaded(false);
          setDraftFadingOut(false);
        }, 500); // Match the CSS animation duration
      }, 45000); // 45 seconds (between 30s-1min)

      return () => clearTimeout(fadeTimer); // Cleanup on unmount
    }
  }, [draftLoaded]);

  // Save draft to localStorage whenever formData changes
  useEffect(() => {
    // Only save if there's some data filled in (not just the initial state)
    const hasData = formData.first_name || formData.last_name || formData.email || 
                    formData.mobile_no || formData.school_year;
    if (hasData) {
      localStorage.setItem('fullApplicationDraft', JSON.stringify(formData));
    }
  }, [formData]);

  const stepTitles = [
    'Application Details',
    'Personal Information',
    'School Information',
    'Educational Background',
    'Parents / Family Information'
  ];

  const handleInputChange = (field: keyof ApplicationData, value: any) => {
    setFormData(prev => {
      // Fields that should NOT be converted to uppercase (numbers, dates, emails, and dropdown selections)
      const excludedFields = [
        'email', 
        'facebook_link', 
        'date_of_birth', 
        'age', 
        'mobile_no', 
        'other_contact',
        'father_contact',
        'mother_contact',
        'zip_code',
        'units_enrolled',
        'course_duration',
        'years_of_residency',
        'swa_input',
        'semesters_to_graduate',
        'shs_years',
        'jhs_years',
        'elem_years',
        // Dropdown/select fields
        'school_year',
        'semester',
        'applying_for_merit',
        'sex',
        'marital_status',
        'religion',
        'ladderized',
        'year_level',
        'graduating_this_term',
        'with_honors',
        'transferee',
        'shiftee',
        'status',
        'shs_type',
        'jhs_type',
        'elem_type',
        'father_education',
        'mother_education',
        'father_deceased',
        'mother_deceased',
        'application_type',
        'scholarship_type'
      ];
      
      // Convert to uppercase if it's a string field and not excluded
      let processedValue = value;
      if (typeof value === 'string' && !excludedFields.includes(field)) {
        processedValue = value.toUpperCase();
      }
      
      const updated = { ...prev, [field]: processedValue };
      
      // Auto-calculate age when date of birth changes
      if (field === 'date_of_birth' && value) {
        const birthDate = new Date(value);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
          age--;
        }
        
        updated.age = age.toString();
      }
      
      return updated;
    });
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      setShowReview(true);
    }
    
    // Scroll to top of the content area
    setTimeout(() => {
      const contentArea = document.querySelector('.application-content');
      if (contentArea) {
        contentArea.scrollTop = 0;
      }
    }, 0);
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
    
    // Scroll to top of the content area
    setTimeout(() => {
      const contentArea = document.querySelector('.application-content');
      if (contentArea) {
        contentArea.scrollTop = 0;
      }
    }, 0);
  };

  const handleSubmit = async () => {
    setShowConfirmDialog(false);
    setIsSubmitting(true);

    try {
      // Map semester format from frontend to backend
      const semesterMap: { [key: string]: string } = {
        '1ST SEMESTER': '1st',
        '2ND SEMESTER': '2nd',
        'SUMMER': 'summer'
      };

      // Map application type
      const applicationTypeMap: { [key: string]: string } = {
        'new': 'new',
        'renewing': 'renewal'
      };

      // Prepare ALL the form data to send to backend API
      const applicationData = {
        // Application Details
        facebook_link: formData.facebook_link,
        application_type: applicationTypeMap[applicantType] || applicantType,
        scholarship_type: formData.scholarship_type,
        school_year: formData.school_year,
        semester: semesterMap[formData.semester] || formData.semester.toLowerCase(),
        applying_for_merit: formData.applying_for_merit,
        
        // Personal Information
        first_name: formData.first_name,
        middle_name: formData.middle_name,
        last_name: formData.last_name,
        house_no: formData.house_no,
        street: formData.street,
        zip_code: formData.zip_code,
        barangay: formData.barangay,
        district: formData.district,
        mobile_no: formData.mobile_no,
        other_contact: formData.other_contact,
        email: formData.email,
        date_of_birth: formData.date_of_birth,
        age: parseInt(formData.age) || null,
        citizenship: formData.citizenship,
        sex: formData.sex,
        marital_status: formData.marital_status,
        religion: formData.religion,
        place_of_birth: formData.place_of_birth,
        years_of_residency: formData.years_of_residency,
        
        // School Information
        course_name: formData.course_name,
        ladderized: formData.ladderized,
        year_level: formData.year_level,
        swa_input: formData.swa_input,
        units_enrolled: formData.units_enrolled,
        course_duration: formData.course_duration,
        school_name: formData.school_name,
        school_address: formData.school_address,
        graduating_this_term: formData.graduating_this_term,
        semesters_to_graduate: formData.semesters_to_graduate,
        with_honors: formData.with_honors,
        transferee: formData.transferee,
        shiftee: formData.shiftee,
        status: formData.status,
        
        // Educational Background
        shs_attended: formData.shs_attended,
        shs_type: formData.shs_type,
        shs_address: formData.shs_address,
        shs_years: formData.shs_years,
        shs_honors: formData.shs_honors,
        jhs_attended: formData.jhs_attended,
        jhs_type: formData.jhs_type,
        jhs_address: formData.jhs_address,
        jhs_years: formData.jhs_years,
        jhs_honors: formData.jhs_honors,
        elem_attended: formData.elem_attended,
        elem_type: formData.elem_type,
        elem_address: formData.elem_address,
        elem_years: formData.elem_years,
        elem_honors: formData.elem_honors,
        
        // Parents Information
        father_name: formData.father_name,
        father_address: formData.father_address,
        father_contact: formData.father_contact,
        father_occupation: formData.father_occupation,
        father_place_of_work: formData.father_place_of_work,
        father_education: formData.father_education,
        father_deceased: formData.father_deceased,
        mother_name: formData.mother_name,
        mother_address: formData.mother_address,
        mother_contact: formData.mother_contact,
        mother_occupation: formData.mother_occupation,
        mother_place_of_work: formData.mother_place_of_work,
        mother_education: formData.mother_education,
        mother_deceased: formData.mother_deceased,
        
        // Status
        is_submitted: true,
        is_locked: true
      };

      console.log('📤 Submitting application data:', applicationData);
      console.log('📊 Data keys:', Object.keys(applicationData));
      console.log('📊 Data field count:', Object.keys(applicationData).length);

      // Submit to backend API
      const response = await apiClient.post('/full-application/', applicationData);
      
      console.log('✅ Application submitted successfully:', response.data);
      console.log('✅ Response status:', response.status);

      // Clear the draft from localStorage after successful submission
      localStorage.removeItem('fullApplicationDraft');

      setIsSubmitting(false);
      // Directly complete
      onComplete({
        school_year: formData.school_year,
        semester: formData.semester
      });
    } catch (error: any) {
      console.error('❌ Error submitting full application:', error);
      console.error('Error response:', error.response);
      console.error('Error data:', error.response?.data);
      setIsSubmitting(false);
      
      // Better error message formatting
      let errorMessage = '';
      
      if (error.response?.data) {
        const data = error.response.data;
        
        // Handle the case where backend returns {success: false, errors: {...}}
        if (data.success === false && data.errors) {
          const errorObj = data.errors;
          errorMessage = Object.entries(errorObj).map(([field, messages]) => {
            const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let errorMsg = '';
            if (Array.isArray(messages)) {
              errorMsg = messages.join(', ');
            } else if (typeof messages === 'object') {
              errorMsg = JSON.stringify(messages);
            } else {
              errorMsg = String(messages);
            }
            return `• ${fieldName}: ${errorMsg}`;
          }).join('\n');
        }
        // If it's a validation error object with field-specific errors
        else if (typeof data === 'object' && !data.error && !data.detail && !data.message) {
          errorMessage = Object.entries(data).map(([field, messages]) => {
            const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let errorMsg = '';
            if (Array.isArray(messages)) {
              errorMsg = messages.join(', ');
            } else if (typeof messages === 'object') {
              errorMsg = JSON.stringify(messages);
            } else {
              errorMsg = String(messages);
            }
            return `• ${fieldName}: ${errorMsg}`;
          }).join('\n');
        } 
        // Handle standard error/detail/message fields
        else {
          errorMessage = data.error || data.detail || data.message || JSON.stringify(data);
        }
      } else {
        errorMessage = error.message || 'Network error - please check your connection';
      }
      
      // Show error dialog with formatted message
      alert('Failed to submit application. Please check the following:\n\n' + (errorMessage || 'Unknown error occurred. Please try again.'));
    }
  };

  const renderStep1 = () => (
    <div className="faf-step-content">
      <div className="faf-step-header">
        <h2>Application Details</h2>
        <p>Please provide your basic application information</p>
      </div>

      <div className="faf-form-section">
        <div className="faf-section-title">
          <h3>Social Media</h3>
        </div>
        <div className="faf-form-grid single-column">
          <div className="faf-form-group">
            <label>Your personalized link on Facebook <span className="faf-required">*</span></label>
            <input
              type="text"
              placeholder="https://facebook.com/your.profile"
              value={formData.facebook_link}
              onChange={(e) => handleInputChange('facebook_link', e.target.value)}
            />
            <span className="faf-helper-text">Enter your Facebook profile URL</span>
          </div>
        </div>
      </div>

      <div className="faf-form-section">
        <div className="faf-section-title">
          <h3>Application Type & Scholarship</h3>
        </div>
        <div className="faf-form-grid">
          <div className="faf-form-group">
            <label>Application Type <span className="faf-required">*</span></label>
            <input type="text" value={formData.application_type} disabled />
          </div>
          <div className="faf-form-group">
            <label>Scholarship Type <span className="faf-required">*</span></label>
            <input type="text" value={formData.scholarship_type} disabled />
          </div>
        </div>
      </div>

      <div className="faf-form-section">
        <div className="faf-section-title">
          <h3>Academic Period</h3>
        </div>
        <div className="faf-form-grid three-columns">
          <div className="faf-form-group">
            <label>School Year <span className="faf-required">*</span></label>
            <select value={formData.school_year} onChange={(e) => handleInputChange('school_year', e.target.value)}>
              <option value="">Select School Year</option>
              <option value="S.Y 2025-2026">S.Y 2025-2026</option>
              <option value="S.Y 2026-2027">S.Y 2026-2027</option>
            </select>
          </div>
          <div className="faf-form-group">
            <label>Semester <span className="faf-required">*</span></label>
            <select value={formData.semester} onChange={(e) => handleInputChange('semester', e.target.value)}>
              <option value="">Select Semester</option>
              <option value="1ST SEMESTER">1ST SEMESTER</option>
              <option value="2ND SEMESTER">2ND SEMESTER</option>
            </select>
          </div>
          <div className="faf-form-group">
            <label>Applying for Merit Incentive? <span className="faf-required">*</span></label>
            <select value={formData.applying_for_merit} onChange={(e) => handleInputChange('applying_for_merit', e.target.value)}>
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </div>
        </div>
        <div className="faf-info-box">
          <div className="faf-info-box-content">
            <p>Merit Incentive is available for students with GWA of 1.75 or higher</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="faf-form-step">
      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>First Name: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Juan"
            value={formData.first_name}
            onChange={(e) => handleInputChange('first_name', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Middle Name <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Santos"
            value={formData.middle_name}
            onChange={(e) => handleInputChange('middle_name', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Last Name <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Dela Cruz"
            value={formData.last_name}
            onChange={(e) => handleInputChange('last_name', e.target.value)}
          />
        </div>
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>House no., Block, Lot, Etc.:<span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Blk/Lot/Unit (e.g., Blk 5 Lot 6)"
            value={formData.house_no}
            onChange={(e) => handleInputChange('house_no', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Street, Village, Etc.: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Street/Village (e.g., Maharlika Village)"
            value={formData.street}
            onChange={(e) => handleInputChange('street', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Zip Code: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="1630"
            value={formData.zip_code}
            onChange={(e) => handleInputChange('zip_code', e.target.value)}
          />
        </div>
      </div>

      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Barangay <span className="faf-required">*</span></label>
          <input
            list="barangay-list"
            type="text"
            placeholder="Search or select barangay"
            value={formData.barangay}
            onChange={(e) => handleInputChange('barangay', e.target.value)}
          />
          <datalist id="barangay-list">
            <option value="Bagumbayan" />
            <option value="Bambang" />
            <option value="Calzada" />
            <option value="Central Bicutan" />
            <option value="Central Signal Village" />
            <option value="Fort Bonifacio" />
            <option value="Hagonoy" />
            <option value="Ibayo-Tipas" />
            <option value="Katuparan" />
            <option value="Ligid-Tipas" />
            <option value="Lower Bicutan" />
            <option value="Maharlika Village" />
            <option value="Napindan" />
            <option value="New Lower Bicutan" />
            <option value="North Daang Hari" />
            <option value="North Signal Village" />
            <option value="Palingon" />
            <option value="Pinagsama" />
            <option value="San Miguel" />
            <option value="Santa Ana" />
            <option value="South Daang Hari" />
            <option value="South Signal Village" />
            <option value="Tanyag" />
            <option value="Tuktukan" />
            <option value="Upper Bicutan" />
            <option value="Ususan" />
            <option value="Wawa" />
            <option value="Western Bicutan" />
          </datalist>
        </div>
        <div className="faf-form-group">
          <label>District <span className="faf-required">*</span></label>
          <input 
            type="text" 
            placeholder="e.g., 1st District" 
            value={formData.district} 
            onChange={(e) => handleInputChange('district', e.target.value)}
          />
        </div>
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Mobile No. <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="11 digits number"
            value={formData.mobile_no}
            onChange={(e) => handleInputChange('mobile_no', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Other Contact No. (Input N/A if not available) <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="N/A"
            value={formData.other_contact}
            onChange={(e) => handleInputChange('other_contact', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Email Address <span className="faf-required">*</span></label>
          <input
            type="email"
            placeholder="name@gmail.com"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
          />
        </div>
      </div>

      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Date of Birth <span className="faf-required">*</span></label>
          <input
            type="date"
            value={formData.date_of_birth}
            onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Age <span className="faf-required">*</span></label>
          <input 
            type="text" 
            placeholder="Auto-calculated" 
            value={formData.age} 
            readOnly 
            className="disabled-input" 
          />
        </div>
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Citizenship <span className="faf-required">*</span></label>
          <input
            type="text"
            value={formData.citizenship}
            onChange={(e) => handleInputChange('citizenship', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Sex <span className="faf-required">*</span></label>
          <select value={formData.sex} onChange={(e) => handleInputChange('sex', e.target.value)}>
            <option value="">Select</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>Marital Status <span className="faf-required">*</span></label>
          <select value={formData.marital_status} onChange={(e) => handleInputChange('marital_status', e.target.value)}>
            <option value="">Select</option>
            <option value="Single">Single</option>
            <option value="Married">Married</option>
            <option value="Widowed">Widowed</option>
            <option value="Separated">Separated</option>
          </select>
        </div>
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Religion <span className="faf-required">*</span></label>
          <select value={formData.religion} onChange={(e) => handleInputChange('religion', e.target.value)}>
            <option value="">Select</option>
            <option value="Roman Catholic">Roman Catholic</option>
            <option value="Islam">Islam</option>
            <option value="Iglesia ni Cristo">Iglesia ni Cristo</option>
            <option value="Protestant">Protestant</option>
            <option value="Others">Others</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>Place of Birth <span className="faf-required">*</span></label>
          <input
            type="text"
            value={formData.place_of_birth}
            onChange={(e) => handleInputChange('place_of_birth', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Years of Residency in Taguig <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 10"
            value={formData.years_of_residency}
            onChange={(e) => handleInputChange('years_of_residency', e.target.value)}
          />
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="faf-form-step">
      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Course Name: <span className="faf-required">*</span></label>
          <input
            list="course-list"
            type="text"
            placeholder="Search or select course"
            value={formData.course_name}
            onChange={(e) => handleInputChange('course_name', e.target.value)}
          />
          <datalist id="course-list">
            <option value="Bachelor of Science in Accountancy" />
            <option value="Bachelor of Science in Business Administration major in Financial Management" />
            <option value="Bachelor of Science in Business Administration major in Human Resource Development Management" />
            <option value="Bachelor of Science in Business Administration major in Marketing Management" />
            <option value="Bachelor of Science in Entrepreneurship" />
            <option value="Bachelor of Science in Office Administration" />
            <option value="Bachelor of Science in Civil Engineering" />
            <option value="Bachelor of Science in Computer Engineering" />
            <option value="Bachelor of Science in Electrical Engineering" />
            <option value="Bachelor of Science in Electronics Engineering" />
            <option value="Bachelor of Science in Mechanical Engineering" />
            <option value="Bachelor of Science in Architecture" />
            <option value="Bachelor of Science in Computer Science" />
            <option value="Bachelor of Science in Information Technology" />
            <option value="Bachelor of Science in Environmental Science" />
            <option value="Bachelor of Science in Food Technology" />
            <option value="Bachelor of Science in Hotel and Restaurant Management" />
            <option value="Bachelor of Science in Tourism Management" />
            <option value="Bachelor of Arts in Communication" />
            <option value="Bachelor of Elementary Education" />
            <option value="Bachelor of Secondary Education major in English" />
            <option value="Bachelor of Secondary Education major in Filipino" />
            <option value="Bachelor of Secondary Education major in Mathematics" />
            <option value="Bachelor of Secondary Education major in Science" />
            <option value="Bachelor of Secondary Education major in Social Studies" />
            <option value="Bachelor of Physical Education" />
            <option value="Bachelor of Public Administration" />
            <option value="Bachelor of Science in Psychology" />
            <option value="Bachelor of Science in Social Work" />
            <option value="Bachelor of Science in Nursing" />
          </datalist>
        </div>
        <div className="faf-form-group">
          <label>Ladderized: <span className="faf-required">*</span></label>
          <select value={formData.ladderized} onChange={(e) => handleInputChange('ladderized', e.target.value)}>
            <option value="YES">YES</option>
            <option value="NO">NO</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>Year Level: <span className="faf-required">*</span></label>
          <select value={formData.year_level} onChange={(e) => handleInputChange('year_level', e.target.value)}>
            <option value="">Select</option>
            <option value="1st Year">1st Year</option>
            <option value="2nd Year">2nd Year</option>
            <option value="3rd Year">3rd Year</option>
            <option value="4th Year">4th Year</option>
            <option value="5th Year">5th Year</option>
          </select>
        </div>
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>SWA Input: <span className="faf-required">*</span></label>
          <input 
            type="text" 
            placeholder="Enter SWA Input" 
            value={formData.swa_input} 
            onChange={(e) => handleInputChange('swa_input', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Units Enrolled: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 18"
            value={formData.units_enrolled}
            onChange={(e) => handleInputChange('units_enrolled', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Course Duration: <span className="faf-required">*</span></label>
          <select value={formData.course_duration} onChange={(e) => handleInputChange('course_duration', e.target.value)}>
            <option value="">Select</option>
            <option value="4 Years">4 Years</option>
            <option value="5 Years">5 Years</option>
          </select>
        </div>
      </div>

      <div className="faf-form-row">
        <div className="faf-form-group">
          <label>School Name: <span className="faf-required">*</span></label>
          <input type="text" value={formData.school_name} disabled className="disabled-input" />
        </div>
      </div>

      <div className="faf-form-row">
        <div className="faf-form-group">
          <label>School Address: <span className="faf-required">*</span></label>
          <input type="text" value={formData.school_address} disabled className="disabled-input" />
        </div>
      </div>

      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Are you graduating this semester/term? <span className="faf-required">*</span></label>
          <select value={formData.graduating_this_term} onChange={(e) => handleInputChange('graduating_this_term', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        {formData.graduating_this_term === 'Yes' && (
          <div className="faf-form-group">
            <label>With Honors? <span className="faf-required">*</span></label>
            <select value={formData.with_honors} onChange={(e) => handleInputChange('with_honors', e.target.value)}>
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </div>
        )}
        {formData.graduating_this_term === 'No' && (
          <div className="faf-form-group">
            <label>How many semester/s more? <span className="faf-required">*</span></label>
            <input
              type="text"
              placeholder="e.g., 2"
              value={formData.semesters_to_graduate}
              onChange={(e) => handleInputChange('semesters_to_graduate', e.target.value)}
            />
          </div>
        )}
      </div>

      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Transferee? <span className="faf-required">*</span></label>
          <select value={formData.transferee} onChange={(e) => handleInputChange('transferee', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>Shiftee? <span className="faf-required">*</span></label>
          <select value={formData.shiftee} onChange={(e) => handleInputChange('shiftee', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>Status: <span className="faf-required">*</span></label>
          <select value={formData.status} onChange={(e) => handleInputChange('status', e.target.value)}>
            <option value="">Select</option>
            <option value="Regular">Regular</option>
            <option value="Irregular">Irregular</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="faf-form-step">
      <h3 className="faf-section-title">Senior High School</h3>
      <div className="faf-form-row">
        <div className="faf-form-group">
          <label>Name of School Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.shs_attended}
            onChange={(e) => handleInputChange('shs_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Type of School: <span className="faf-required">*</span></label>
          <select value={formData.shs_type} onChange={(e) => handleInputChange('shs_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>School Address: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.shs_address}
            onChange={(e) => handleInputChange('shs_address', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Years Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2017-2019"
            value={formData.shs_years}
            onChange={(e) => handleInputChange('shs_years', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Honors Received: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Input N/A if not available"
            value={formData.shs_honors}
            onChange={(e) => handleInputChange('shs_honors', e.target.value)}
          />
        </div>
      </div>

      <h3 className="faf-section-title">Junior High School / ALS</h3>
      <div className="faf-form-row">
        <div className="faf-form-group">
          <label>Name of School Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.jhs_attended}
            onChange={(e) => handleInputChange('jhs_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Type of School: <span className="faf-required">*</span></label>
          <select value={formData.jhs_type} onChange={(e) => handleInputChange('jhs_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>School Address: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.jhs_address}
            onChange={(e) => handleInputChange('jhs_address', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Years Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2015-2017"
            value={formData.jhs_years}
            onChange={(e) => handleInputChange('jhs_years', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Honors Received: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Input N/A if not available"
            value={formData.jhs_honors}
            onChange={(e) => handleInputChange('jhs_honors', e.target.value)}
          />
        </div>
      </div>

      <h3 className="faf-section-title">Elementary</h3>
      <div className="faf-form-row">
        <div className="faf-form-group">
          <label>Name of School Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.elem_attended}
            onChange={(e) => handleInputChange('elem_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Type of School: <span className="faf-required">*</span></label>
          <select value={formData.elem_type} onChange={(e) => handleInputChange('elem_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label>School Address: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.elem_address}
            onChange={(e) => handleInputChange('elem_address', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Years Attended: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2009-2015"
            value={formData.elem_years}
            onChange={(e) => handleInputChange('elem_years', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Honors Received: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Input N/A if not available"
            value={formData.elem_honors}
            onChange={(e) => handleInputChange('elem_honors', e.target.value)}
          />
        </div>
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="faf-form-step">
      <h3 className="faf-section-title">Father's Information</h3>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Complete Name: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Father's Full Name"
            value={formData.father_name}
            onChange={(e) => handleInputChange('father_name', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Address: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Complete Address"
            value={formData.father_address}
            onChange={(e) => handleInputChange('father_address', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Contact No.: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Mobile Number"
            value={formData.father_contact}
            onChange={(e) => handleInputChange('father_contact', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Occupation: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Job/Profession"
            value={formData.father_occupation}
            onChange={(e) => handleInputChange('father_occupation', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Place of Work: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Workplace"
            value={formData.father_place_of_work}
            onChange={(e) => handleInputChange('father_place_of_work', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Highest Educational Attainment: <span className="faf-required">*</span></label>
          <select value={formData.father_education} onChange={(e) => handleInputChange('father_education', e.target.value)}>
            <option value="">Select</option>
            <option value="Elementary">Elementary</option>
            <option value="High School">High School</option>
            <option value="Senior High School">Senior High School</option>
            <option value="College Graduate">College Graduate</option>
            <option value="Vocational">Vocational</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.father_deceased}
              onChange={(e) => handleInputChange('father_deceased', e.target.checked)}
            />
            <span>Check if deceased</span>
          </label>
        </div>
      </div>

      <h3 className="faf-section-title">Mother's Information</h3>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Complete Name: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Mother's Full Name"
            value={formData.mother_name}
            onChange={(e) => handleInputChange('mother_name', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Address: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Complete Address"
            value={formData.mother_address}
            onChange={(e) => handleInputChange('mother_address', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row three-cols">
        <div className="faf-form-group">
          <label>Contact No.: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Mobile Number"
            value={formData.mother_contact}
            onChange={(e) => handleInputChange('mother_contact', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Occupation: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Job/Profession"
            value={formData.mother_occupation}
            onChange={(e) => handleInputChange('mother_occupation', e.target.value)}
          />
        </div>
        <div className="faf-form-group">
          <label>Place of Work: <span className="faf-required">*</span></label>
          <input
            type="text"
            placeholder="Workplace"
            value={formData.mother_place_of_work}
            onChange={(e) => handleInputChange('mother_place_of_work', e.target.value)}
          />
        </div>
      </div>
      <div className="faf-form-row two-cols">
        <div className="faf-form-group">
          <label>Highest Educational Attainment: <span className="faf-required">*</span></label>
          <select value={formData.mother_education} onChange={(e) => handleInputChange('mother_education', e.target.value)}>
            <option value="">Select</option>
            <option value="Elementary">Elementary</option>
            <option value="High School">High School</option>
            <option value="Senior High School">Senior High School</option>
            <option value="College Graduate">College Graduate</option>
            <option value="Vocational">Vocational</option>
          </select>
        </div>
        <div className="faf-form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.mother_deceased}
              onChange={(e) => handleInputChange('mother_deceased', e.target.checked)}
            />
            <span>Check if deceased</span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderReviewPage = () => (
    <div className="review-page">
      <h2>Review Your Application</h2>
      <p className="review-instruction">Please review all information carefully before submitting.</p>

      <div className="faf-review-section">
        <h3>Application Details</h3>
        <div className="review-item"><strong>Facebook Link:</strong> {formData.facebook_link}</div>
        <div className="review-item"><strong>Application Type:</strong> {formData.application_type}</div>
        <div className="review-item"><strong>Scholarship Type:</strong> {formData.scholarship_type}</div>
        <div className="review-item"><strong>School Year:</strong> {formData.school_year}</div>
        <div className="review-item"><strong>Semester:</strong> {formData.semester}</div>
        <div className="review-item"><strong>Applying for Merit:</strong> {formData.applying_for_merit}</div>
      </div>

      <div className="faf-review-section">
        <h3>Personal Information</h3>
        <div className="review-item"><strong>Name:</strong> {formData.first_name} {formData.middle_name} {formData.last_name}</div>
        <div className="review-item"><strong>Address:</strong> {formData.house_no}, {formData.street}, {formData.barangay}, Taguig City {formData.zip_code}</div>
        <div className="review-item"><strong>Contact:</strong> {formData.mobile_no} / {formData.other_contact}</div>
        <div className="review-item"><strong>Email:</strong> {formData.email}</div>
        <div className="review-item"><strong>Date of Birth:</strong> {formData.date_of_birth}</div>
        <div className="review-item"><strong>Sex:</strong> {formData.sex}</div>
        <div className="review-item"><strong>Marital Status:</strong> {formData.marital_status}</div>
        <div className="review-item"><strong>Religion:</strong> {formData.religion}</div>
      </div>

      <div className="faf-review-section">
        <h3>School Information</h3>
        <div className="review-item"><strong>Course:</strong> {formData.course_name}</div>
        <div className="review-item"><strong>Year Level:</strong> {formData.year_level}</div>
        <div className="review-item"><strong>Units Enrolled:</strong> {formData.units_enrolled}</div>
        <div className="review-item"><strong>School:</strong> {formData.school_name}</div>
        <div className="review-item"><strong>Graduating:</strong> {formData.graduating_this_term}</div>
      </div>

      <div className="faf-review-section">
        <div className="faf-review-header">
          <h3>Educational Background</h3>
        </div>
        <div className="faf-review-grid">
          <div className="faf-review-item full-width" style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '12px', marginBottom: '12px' }}>
            <div className="faf-review-label">SENIOR HIGH SCHOOL</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">School Name</div>
            <div className="faf-review-value">{formData.shs_attended || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Type</div>
            <div className="faf-review-value">{formData.shs_type || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Years Attended</div>
            <div className="faf-review-value">{formData.shs_years || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Address</div>
            <div className="faf-review-value">{formData.shs_address || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Honors/Awards</div>
            <div className="faf-review-value">{formData.shs_honors || 'None'}</div>
          </div>

          <div className="faf-review-item full-width" style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '12px', marginBottom: '12px', marginTop: '20px' }}>
            <div className="faf-review-label">JUNIOR HIGH SCHOOL</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">School Name</div>
            <div className="faf-review-value">{formData.jhs_attended || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Type</div>
            <div className="faf-review-value">{formData.jhs_type || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Years Attended</div>
            <div className="faf-review-value">{formData.jhs_years || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Address</div>
            <div className="faf-review-value">{formData.jhs_address || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Honors/Awards</div>
            <div className="faf-review-value">{formData.jhs_honors || 'None'}</div>
          </div>

          <div className="faf-review-item full-width" style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '12px', marginBottom: '12px', marginTop: '20px' }}>
            <div className="faf-review-label">ELEMENTARY</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">School Name</div>
            <div className="faf-review-value">{formData.elem_attended || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Type</div>
            <div className="faf-review-value">{formData.elem_type || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Years Attended</div>
            <div className="faf-review-value">{formData.elem_years || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Address</div>
            <div className="faf-review-value">{formData.elem_address || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Honors/Awards</div>
            <div className="faf-review-value">{formData.elem_honors || 'None'}</div>
          </div>
        </div>
      </div>

      <div className="faf-review-section">
        <div className="faf-review-header">
          <h3>Parents Information</h3>
        </div>
        <div className="faf-review-grid">
          <div className="faf-review-item full-width" style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '12px', marginBottom: '12px' }}>
            <div className="faf-review-label">FATHER'S INFORMATION</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Full Name</div>
            <div className="faf-review-value">{formData.father_name || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Contact Number</div>
            <div className="faf-review-value">{formData.father_contact || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Address</div>
            <div className="faf-review-value">{formData.father_address || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Occupation</div>
            <div className="faf-review-value">{formData.father_occupation || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Place of Work</div>
            <div className="faf-review-value">{formData.father_place_of_work || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Educational Attainment</div>
            <div className="faf-review-value">{formData.father_education || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Status</div>
            <div className="faf-review-value">{formData.father_deceased ? '† Deceased' : 'Living'}</div>
          </div>

          <div className="faf-review-item full-width" style={{ borderBottom: '2px solid #e5e7eb', paddingBottom: '12px', marginBottom: '12px', marginTop: '20px' }}>
            <div className="faf-review-label">MOTHER'S INFORMATION</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Full Name</div>
            <div className="faf-review-value">{formData.mother_name || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Contact Number</div>
            <div className="faf-review-value">{formData.mother_contact || 'Not provided'}</div>
          </div>
          <div className="faf-review-item full-width">
            <div className="faf-review-label">Address</div>
            <div className="faf-review-value">{formData.mother_address || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Occupation</div>
            <div className="faf-review-value">{formData.mother_occupation || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Place of Work</div>
            <div className="faf-review-value">{formData.mother_place_of_work || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Educational Attainment</div>
            <div className="faf-review-value">{formData.mother_education || 'Not provided'}</div>
          </div>
          <div className="faf-review-item">
            <div className="faf-review-label">Status</div>
            <div className="faf-review-value">{formData.mother_deceased ? '† Deceased' : 'Living'}</div>
          </div>
        </div>
      </div>

      <div className="faf-review-actions">
        <button className="faf-btn-edit" onClick={() => setShowReview(false)}>Edit Application</button>
        <button className="faf-btn-submit-final" onClick={() => setShowConfirmDialog(true)}>Submit Application</button>
      </div>
    </div>
  );

  // Show loading while checking for existing application
  if (checkingExisting) {
    return (
      <div className="faf-overlay">
        <div className="faf-container">
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Checking for existing application...</p>
          </div>
        </div>
      </div>
    );
  }

  // Don't render form if user already has an application
  if (hasExistingApplication) {
    return null;
  }

  return (
    <div className="faf-overlay">
      <div className="faf-container">
        {isSubmitting && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Submitting your application...</p>
          </div>
        )}

        <div className="faf-header">
          <div className="faf-header-content">
            <div className="faf-header-title">
              <div className="faf-header-text">
                <h1>TCU-CEAA Application Form</h1>
                <p>{applicantType === 'new' ? 'New Applicant' : 'Renewing Applicant'} • {new Date().getFullYear()}</p>
              </div>
            </div>
            <button className="faf-close-btn" onClick={onCancel}>×</button>
          </div>
        </div>

            {draftLoaded && (
              <div className={`faf-draft-notification ${draftFadingOut ? 'fade-out' : ''}`}>
                <span className="faf-draft-notification-text">
                  ✅ Draft restored! Your previous application data has been loaded.
                </span>
                <button
                  className="faf-draft-clear-btn"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to clear your saved draft? This cannot be undone.')) {
                      localStorage.removeItem('fullApplicationDraft');
                      window.location.reload();
                    }
                  }}
                >
                  Clear Draft
                </button>
              </div>
            )}

            {!showReview && (
              <div className="faf-progress">
                <div className="faf-progress-steps">
                  <div className="faf-progress-line">
                    <div className="faf-progress-line-fill" style={{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }}></div>
                  </div>
                  {stepTitles.map((title, index) => (
                    <div key={index} className={`faf-progress-step ${index + 1 === currentStep ? 'active' : ''} ${index + 1 < currentStep ? 'completed' : ''}`}>
                      <div className={`faf-step-circle ${index + 1 < currentStep ? 'checkmark' : ''}`}>
                        {index + 1 < currentStep ? '' : index + 1}
                      </div>
                      <div className="faf-step-label">{title}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="faf-content">
              {showReview ? (
                renderReviewPage()
              ) : (
                <>
                  {currentStep === 1 && renderStep1()}
                  {currentStep === 2 && renderStep2()}
                  {currentStep === 3 && renderStep3()}
                  {currentStep === 4 && renderStep4()}
                  {currentStep === 5 && renderStep5()}
                </>
              )}
            </div>

            {!showReview && (
              <div className="faf-footer">
                <div className="faf-footer-info">
                  Step {currentStep} of {totalSteps}
                </div>
                <div className="faf-footer-buttons">
                  {currentStep > 1 && (
                    <button className="faf-btn btn-secondary" onClick={handlePrevious}>
                      <span className="faf-btn-icon">←</span>
                      Previous
                    </button>
                  )}
                  <button className="faf-btn btn-primary" onClick={handleNext}>
                    {currentStep === totalSteps ? 'Review Application' : 'Next'}
                    <span className="faf-btn-icon">→</span>
                  </button>
                </div>
              </div>
            )}

        {showConfirmDialog && (
          <div className="faf-confirm-dialog-overlay">
            <div className="faf-confirm-dialog">
              <div className="faf-dialog-icon">⚠️</div>
              <h3>Confirm Application Submission</h3>
              <p>Once submitted, your application will be locked and you will no longer be able to edit the information. Please make sure all details are correct before proceeding.</p>
              <div className="faf-dialog-actions">
                <button className="faf-btn btn-secondary" onClick={() => setShowConfirmDialog(false)}>
                  <span className="faf-btn-icon">←</span>
                  Go Back
                </button>
                <button className="faf-btn btn-primary" onClick={handleSubmit}>
                  <span className="faf-btn-icon">✓</span>
                  Confirm & Submit
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FullApplicationForm;




