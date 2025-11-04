import React, { useState } from 'react';
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
  const [showSuccess, setShowSuccess] = useState(false);
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

  const stepTitles = [
    'Application Details',
    'Personal Information',
    'School Information',
    'Educational Background',
    'Parents / Family Information'
  ];

  const handleInputChange = (field: keyof ApplicationData, value: any) => {
    setFormData(prev => {
      const updated = { ...prev, [field]: value };
      
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
    // Scroll to top of the form
    const formContainer = document.querySelector('.full-application-container');
    if (formContainer) {
      formContainer.scrollTop = 0;
    }
    
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      setShowReview(true);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setShowConfirmDialog(false);
    setIsSubmitting(true);

    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setShowSuccess(true);
      // Pass school year and semester to parent
      setTimeout(() => {
        onComplete({
          school_year: formData.school_year,
          semester: formData.semester
        });
      }, 1500);
    }, 2000);
  };

  const renderStep1 = () => (
    <div className="form-step">
      <div className="form-row">
        <div className="form-group">
          <label>Your personalized link on Facebook: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="https://facebook.com/your.profile"
            value={formData.facebook_link}
            onChange={(e) => handleInputChange('facebook_link', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row two-cols">
        <div className="form-group">
          <label>Application Type: <span className="required">*</span></label>
          <input type="text" value={formData.application_type} disabled className="disabled-input" />
        </div>
        <div className="form-group">
          <label>Scholarship Type: <span className="required">*</span></label>
          <input type="text" value={formData.scholarship_type} disabled className="disabled-input" />
        </div>
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>School Year: <span className="required">*</span></label>
          <select value={formData.school_year} onChange={(e) => handleInputChange('school_year', e.target.value)}>
            <option value="">Select School Year</option>
            <option value="S.Y 2025-2026">S.Y 2025-2026</option>
            <option value="S.Y 2026-2027">S.Y 2026-2027</option>
          </select>
        </div>
        <div className="form-group">
          <label>Semester: <span className="required">*</span></label>
          <select value={formData.semester} onChange={(e) => handleInputChange('semester', e.target.value)}>
            <option value="">Select Semester</option>
            <option value="1ST SEMESTER">1ST SEMESTER</option>
            <option value="2ND SEMESTER">2ND SEMESTER</option>
          </select>
        </div>
        <div className="form-group">
          <label>Applying for Merit Incentive? <span className="required">*</span></label>
          <select value={formData.applying_for_merit} onChange={(e) => handleInputChange('applying_for_merit', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="form-step">
      <div className="form-row three-cols">
        <div className="form-group">
          <label>First Name: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Juan"
            value={formData.first_name}
            onChange={(e) => handleInputChange('first_name', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Middle Name <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Santos"
            value={formData.middle_name}
            onChange={(e) => handleInputChange('middle_name', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Last Name <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Dela Cruz"
            value={formData.last_name}
            onChange={(e) => handleInputChange('last_name', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>House no., Block, Lot, Etc.:<span className="required">*</span></label>
          <input
            type="text"
            placeholder="Blk/Lot/Unit (e.g., Blk 5 Lot 6)"
            value={formData.house_no}
            onChange={(e) => handleInputChange('house_no', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Street, Village, Etc.: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Street/Village (e.g., Maharlika Village)"
            value={formData.street}
            onChange={(e) => handleInputChange('street', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Zip Code: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="1630"
            value={formData.zip_code}
            onChange={(e) => handleInputChange('zip_code', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row two-cols">
        <div className="form-group">
          <label>Barangay <span className="required">*</span></label>
          <select value={formData.barangay} onChange={(e) => handleInputChange('barangay', e.target.value)}>
            <option value="">Select Barangay</option>
            <option value="Bagumbayan">Bagumbayan</option>
            <option value="Bambang">Bambang</option>
            <option value="Calzada">Calzada</option>
            <option value="Central Bicutan">Central Bicutan</option>
            <option value="Central Signal Village">Central Signal Village</option>
            <option value="Fort Bonifacio">Fort Bonifacio</option>
            <option value="Hagonoy">Hagonoy</option>
            <option value="Ibayo-Tipas">Ibayo-Tipas</option>
            <option value="Katuparan">Katuparan</option>
            <option value="Ligid-Tipas">Ligid-Tipas</option>
            <option value="Lower Bicutan">Lower Bicutan</option>
            <option value="Maharlika Village">Maharlika Village</option>
            <option value="Napindan">Napindan</option>
            <option value="New Lower Bicutan">New Lower Bicutan</option>
            <option value="North Daang Hari">North Daang Hari</option>
            <option value="North Signal Village">North Signal Village</option>
            <option value="Palingon">Palingon</option>
            <option value="Pinagsama">Pinagsama</option>
            <option value="San Miguel">San Miguel</option>
            <option value="Santa Ana">Santa Ana</option>
            <option value="South Daang Hari">South Daang Hari</option>
            <option value="South Signal Village">South Signal Village</option>
            <option value="Tanyag">Tanyag</option>
            <option value="Tuktukan">Tuktukan</option>
            <option value="Upper Bicutan">Upper Bicutan</option>
            <option value="Ususan">Ususan</option>
            <option value="Wawa">Wawa</option>
            <option value="Western Bicutan">Western Bicutan</option>
          </select>
        </div>
        <div className="form-group">
          <label>District <span className="required">*</span></label>
          <input 
            type="text" 
            placeholder="e.g., 1st District" 
            value={formData.district} 
            onChange={(e) => handleInputChange('district', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>Mobile No. <span className="required">*</span></label>
          <input
            type="text"
            placeholder="11 digits number"
            value={formData.mobile_no}
            onChange={(e) => handleInputChange('mobile_no', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Other Contact No. (Input N/A if not available) <span className="required">*</span></label>
          <input
            type="text"
            placeholder="N/A"
            value={formData.other_contact}
            onChange={(e) => handleInputChange('other_contact', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Email Address <span className="required">*</span></label>
          <input
            type="email"
            placeholder="name@gmail.com"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
          />
        </div>
      </div>

      <div className="form-row two-cols">
        <div className="form-group">
          <label>Date of Birth <span className="required">*</span></label>
          <input
            type="date"
            value={formData.date_of_birth}
            onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Age <span className="required">*</span></label>
          <input 
            type="text" 
            placeholder="Auto-calculated" 
            value={formData.age} 
            readOnly 
            className="disabled-input" 
          />
        </div>
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>Citizenship <span className="required">*</span></label>
          <input
            type="text"
            value={formData.citizenship}
            onChange={(e) => handleInputChange('citizenship', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Sex <span className="required">*</span></label>
          <select value={formData.sex} onChange={(e) => handleInputChange('sex', e.target.value)}>
            <option value="">Select</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
        </div>
        <div className="form-group">
          <label>Marital Status <span className="required">*</span></label>
          <select value={formData.marital_status} onChange={(e) => handleInputChange('marital_status', e.target.value)}>
            <option value="">Select</option>
            <option value="Single">Single</option>
            <option value="Married">Married</option>
            <option value="Widowed">Widowed</option>
            <option value="Separated">Separated</option>
          </select>
        </div>
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>Religion <span className="required">*</span></label>
          <select value={formData.religion} onChange={(e) => handleInputChange('religion', e.target.value)}>
            <option value="">Select</option>
            <option value="Roman Catholic">Roman Catholic</option>
            <option value="Islam">Islam</option>
            <option value="Iglesia ni Cristo">Iglesia ni Cristo</option>
            <option value="Protestant">Protestant</option>
            <option value="Others">Others</option>
          </select>
        </div>
        <div className="form-group">
          <label>Place of Birth <span className="required">*</span></label>
          <input
            type="text"
            value={formData.place_of_birth}
            onChange={(e) => handleInputChange('place_of_birth', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Years of Residency in Taguig <span className="required">*</span></label>
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
    <div className="form-step">
      <div className="form-row three-cols">
        <div className="form-group">
          <label>Course Name: <span className="required">*</span></label>
          <select value={formData.course_name} onChange={(e) => handleInputChange('course_name', e.target.value)}>
            <option value="">Select Course</option>
            <optgroup label="College of Business and Accountancy">
              <option value="Bachelor of Science in Accountancy">Bachelor of Science in Accountancy</option>
              <option value="Bachelor of Science in Business Administration major in Financial Management">BS Business Administration major in Financial Management</option>
              <option value="Bachelor of Science in Business Administration major in Human Resource Development Management">BS Business Administration major in Human Resource Development Management</option>
              <option value="Bachelor of Science in Business Administration major in Marketing Management">BS Business Administration major in Marketing Management</option>
              <option value="Bachelor of Science in Entrepreneurship">Bachelor of Science in Entrepreneurship</option>
              <option value="Bachelor of Science in Office Administration">Bachelor of Science in Office Administration</option>
            </optgroup>
            <optgroup label="College of Engineering and Architecture">
              <option value="Bachelor of Science in Civil Engineering">Bachelor of Science in Civil Engineering</option>
              <option value="Bachelor of Science in Computer Engineering">Bachelor of Science in Computer Engineering</option>
              <option value="Bachelor of Science in Electrical Engineering">Bachelor of Science in Electrical Engineering</option>
              <option value="Bachelor of Science in Electronics Engineering">Bachelor of Science in Electronics Engineering</option>
              <option value="Bachelor of Science in Mechanical Engineering">Bachelor of Science in Mechanical Engineering</option>
              <option value="Bachelor of Science in Architecture">Bachelor of Science in Architecture</option>
            </optgroup>
            <optgroup label="College of Science">
              <option value="Bachelor of Science in Computer Science">Bachelor of Science in Computer Science</option>
              <option value="Bachelor of Science in Information Technology">Bachelor of Science in Information Technology</option>
              <option value="Bachelor of Science in Environmental Science">Bachelor of Science in Environmental Science</option>
              <option value="Bachelor of Science in Food Technology">Bachelor of Science in Food Technology</option>
            </optgroup>
            <optgroup label="College of Hospitality and Tourism Management">
              <option value="Bachelor of Science in Hotel and Restaurant Management">Bachelor of Science in Hotel and Restaurant Management</option>
              <option value="Bachelor of Science in Tourism Management">Bachelor of Science in Tourism Management</option>
            </optgroup>
            <optgroup label="College of Liberal Arts, Sciences and Education">
              <option value="Bachelor of Arts in Communication">Bachelor of Arts in Communication</option>
              <option value="Bachelor of Elementary Education">Bachelor of Elementary Education</option>
              <option value="Bachelor of Secondary Education major in English">Bachelor of Secondary Education major in English</option>
              <option value="Bachelor of Secondary Education major in Filipino">Bachelor of Secondary Education major in Filipino</option>
              <option value="Bachelor of Secondary Education major in Mathematics">Bachelor of Secondary Education major in Mathematics</option>
              <option value="Bachelor of Secondary Education major in Science">Bachelor of Secondary Education major in Science</option>
              <option value="Bachelor of Secondary Education major in Social Studies">Bachelor of Secondary Education major in Social Studies</option>
              <option value="Bachelor of Physical Education">Bachelor of Physical Education</option>
              <option value="Bachelor of Public Administration">Bachelor of Public Administration</option>
              <option value="Bachelor of Science in Psychology">Bachelor of Science in Psychology</option>
              <option value="Bachelor of Science in Social Work">Bachelor of Science in Social Work</option>
            </optgroup>
            <optgroup label="Institute of Health Sciences">
              <option value="Bachelor of Science in Nursing">Bachelor of Science in Nursing</option>
            </optgroup>
          </select>
        </div>
        <div className="form-group">
          <label>Ladderized: <span className="required">*</span></label>
          <select value={formData.ladderized} onChange={(e) => handleInputChange('ladderized', e.target.value)}>
            <option value="YES">YES</option>
            <option value="NO">NO</option>
          </select>
        </div>
        <div className="form-group">
          <label>Year Level: <span className="required">*</span></label>
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

      <div className="form-row three-cols">
        <div className="form-group">
          <label>SWA Input: <span className="required">*</span></label>
          <input 
            type="text" 
            placeholder="Enter SWA Input" 
            value={formData.swa_input} 
            onChange={(e) => handleInputChange('swa_input', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Units Enrolled: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 18"
            value={formData.units_enrolled}
            onChange={(e) => handleInputChange('units_enrolled', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Course Duration: <span className="required">*</span></label>
          <select value={formData.course_duration} onChange={(e) => handleInputChange('course_duration', e.target.value)}>
            <option value="">Select</option>
            <option value="4 Years">4 Years</option>
            <option value="5 Years">5 Years</option>
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>School Name: <span className="required">*</span></label>
          <input type="text" value={formData.school_name} disabled className="disabled-input" />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>School Address: <span className="required">*</span></label>
          <input type="text" value={formData.school_address} disabled className="disabled-input" />
        </div>
      </div>

      <div className="form-row two-cols">
        <div className="form-group">
          <label>Are you graduating this semester/term? <span className="required">*</span></label>
          <select value={formData.graduating_this_term} onChange={(e) => handleInputChange('graduating_this_term', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        {formData.graduating_this_term === 'Yes' && (
          <div className="form-group">
            <label>With Honors? <span className="required">*</span></label>
            <select value={formData.with_honors} onChange={(e) => handleInputChange('with_honors', e.target.value)}>
              <option value="">Select</option>
              <option value="Yes">Yes</option>
              <option value="No">No</option>
            </select>
          </div>
        )}
        {formData.graduating_this_term === 'No' && (
          <div className="form-group">
            <label>How many semester/s more? <span className="required">*</span></label>
            <input
              type="text"
              placeholder="e.g., 2"
              value={formData.semesters_to_graduate}
              onChange={(e) => handleInputChange('semesters_to_graduate', e.target.value)}
            />
          </div>
        )}
      </div>

      <div className="form-row three-cols">
        <div className="form-group">
          <label>Transferee? <span className="required">*</span></label>
          <select value={formData.transferee} onChange={(e) => handleInputChange('transferee', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="form-group">
          <label>Shiftee? <span className="required">*</span></label>
          <select value={formData.shiftee} onChange={(e) => handleInputChange('shiftee', e.target.value)}>
            <option value="">Select</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
        <div className="form-group">
          <label>Status: <span className="required">*</span></label>
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
    <div className="form-step">
      <h3 className="section-title">Senior High School</h3>
      <div className="form-row">
        <div className="form-group">
          <label>Name of School Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.shs_attended}
            onChange={(e) => handleInputChange('shs_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Type of School: <span className="required">*</span></label>
          <select value={formData.shs_type} onChange={(e) => handleInputChange('shs_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="form-group">
          <label>School Address: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.shs_address}
            onChange={(e) => handleInputChange('shs_address', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Years Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2017-2019"
            value={formData.shs_years}
            onChange={(e) => handleInputChange('shs_years', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Honors Received: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Input N/A if not available"
            value={formData.shs_honors}
            onChange={(e) => handleInputChange('shs_honors', e.target.value)}
          />
        </div>
      </div>

      <h3 className="section-title">Junior High School / ALS</h3>
      <div className="form-row">
        <div className="form-group">
          <label>Name of School Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.jhs_attended}
            onChange={(e) => handleInputChange('jhs_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Type of School: <span className="required">*</span></label>
          <select value={formData.jhs_type} onChange={(e) => handleInputChange('jhs_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="form-group">
          <label>School Address: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.jhs_address}
            onChange={(e) => handleInputChange('jhs_address', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Years Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2015-2017"
            value={formData.jhs_years}
            onChange={(e) => handleInputChange('jhs_years', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Honors Received: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Input N/A if not available"
            value={formData.jhs_honors}
            onChange={(e) => handleInputChange('jhs_honors', e.target.value)}
          />
        </div>
      </div>

      <h3 className="section-title">Elementary</h3>
      <div className="form-row">
        <div className="form-group">
          <label>Name of School Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="School Name"
            value={formData.elem_attended}
            onChange={(e) => handleInputChange('elem_attended', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Type of School: <span className="required">*</span></label>
          <select value={formData.elem_type} onChange={(e) => handleInputChange('elem_type', e.target.value)}>
            <option value="">Select</option>
            <option value="Public">Public</option>
            <option value="Private">Private</option>
          </select>
        </div>
        <div className="form-group">
          <label>School Address: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Address"
            value={formData.elem_address}
            onChange={(e) => handleInputChange('elem_address', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Years Attended: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="e.g., 2009-2015"
            value={formData.elem_years}
            onChange={(e) => handleInputChange('elem_years', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Honors Received: <span className="required">*</span></label>
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
    <div className="form-step">
      <h3 className="section-title">Father's Information</h3>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Complete Name: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Father's Full Name"
            value={formData.father_name}
            onChange={(e) => handleInputChange('father_name', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Address: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Complete Address"
            value={formData.father_address}
            onChange={(e) => handleInputChange('father_address', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row three-cols">
        <div className="form-group">
          <label>Contact No.: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Mobile Number"
            value={formData.father_contact}
            onChange={(e) => handleInputChange('father_contact', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Occupation: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Job/Profession"
            value={formData.father_occupation}
            onChange={(e) => handleInputChange('father_occupation', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Place of Work: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Workplace"
            value={formData.father_place_of_work}
            onChange={(e) => handleInputChange('father_place_of_work', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Highest Educational Attainment: <span className="required">*</span></label>
          <select value={formData.father_education} onChange={(e) => handleInputChange('father_education', e.target.value)}>
            <option value="">Select</option>
            <option value="Elementary">Elementary</option>
            <option value="High School">High School</option>
            <option value="Senior High School">Senior High School</option>
            <option value="College Graduate">College Graduate</option>
            <option value="Vocational">Vocational</option>
          </select>
        </div>
        <div className="form-group">
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

      <h3 className="section-title">Mother's Information</h3>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Complete Name: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Mother's Full Name"
            value={formData.mother_name}
            onChange={(e) => handleInputChange('mother_name', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Address: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Complete Address"
            value={formData.mother_address}
            onChange={(e) => handleInputChange('mother_address', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row three-cols">
        <div className="form-group">
          <label>Contact No.: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Mobile Number"
            value={formData.mother_contact}
            onChange={(e) => handleInputChange('mother_contact', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Occupation: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Job/Profession"
            value={formData.mother_occupation}
            onChange={(e) => handleInputChange('mother_occupation', e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Place of Work: <span className="required">*</span></label>
          <input
            type="text"
            placeholder="Workplace"
            value={formData.mother_place_of_work}
            onChange={(e) => handleInputChange('mother_place_of_work', e.target.value)}
          />
        </div>
      </div>
      <div className="form-row two-cols">
        <div className="form-group">
          <label>Highest Educational Attainment: <span className="required">*</span></label>
          <select value={formData.mother_education} onChange={(e) => handleInputChange('mother_education', e.target.value)}>
            <option value="">Select</option>
            <option value="Elementary">Elementary</option>
            <option value="High School">High School</option>
            <option value="Senior High School">Senior High School</option>
            <option value="College Graduate">College Graduate</option>
            <option value="Vocational">Vocational</option>
          </select>
        </div>
        <div className="form-group">
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

      <div className="review-section">
        <h3>Application Details</h3>
        <div className="review-item"><strong>Facebook Link:</strong> {formData.facebook_link}</div>
        <div className="review-item"><strong>Application Type:</strong> {formData.application_type}</div>
        <div className="review-item"><strong>Scholarship Type:</strong> {formData.scholarship_type}</div>
        <div className="review-item"><strong>School Year:</strong> {formData.school_year}</div>
        <div className="review-item"><strong>Semester:</strong> {formData.semester}</div>
        <div className="review-item"><strong>Applying for Merit:</strong> {formData.applying_for_merit}</div>
      </div>

      <div className="review-section">
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

      <div className="review-section">
        <h3>School Information</h3>
        <div className="review-item"><strong>Course:</strong> {formData.course_name}</div>
        <div className="review-item"><strong>Year Level:</strong> {formData.year_level}</div>
        <div className="review-item"><strong>Units Enrolled:</strong> {formData.units_enrolled}</div>
        <div className="review-item"><strong>School:</strong> {formData.school_name}</div>
        <div className="review-item"><strong>Graduating:</strong> {formData.graduating_this_term}</div>
      </div>

      <div className="review-section">
        <h3>Educational Background</h3>
        <div className="review-item"><strong>Senior High:</strong> {formData.shs_attended}</div>
        <div className="review-item"><strong>Junior High:</strong> {formData.jhs_attended}</div>
        <div className="review-item"><strong>Elementary:</strong> {formData.elem_attended}</div>
      </div>

      <div className="review-section">
        <h3>Parents Information</h3>
        <div className="review-item"><strong>Father:</strong> {formData.father_name}</div>
        <div className="review-item"><strong>Mother:</strong> {formData.mother_name}</div>
      </div>

      <div className="review-actions">
        <button className="btn-edit" onClick={() => setShowReview(false)}>Edit Application</button>
        <button className="btn-submit-final" onClick={() => setShowConfirmDialog(true)}>Submit Application</button>
      </div>
    </div>
  );

  return (
    <div className="full-application-overlay">
      <div className="full-application-container">
        {isSubmitting && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Submitting your application...</p>
          </div>
        )}

        {showSuccess ? (
          <div className="success-page">
            <div className="success-icon">✓</div>
            <h2>Information Submitted</h2>
            <p>We will review your application and get back to you shortly.</p>
            <div className="success-buttons">
              <button className="btn-primary" onClick={() => onComplete({ school_year: formData.school_year, semester: formData.semester })}>Go to Dashboard</button>
              <button className="btn-secondary" onClick={() => onComplete({ school_year: formData.school_year, semester: formData.semester })}>Go to Submission of Requirements</button>
            </div>
          </div>
        ) : (
          <>
            <div className="application-header">
              <h1>TCU-CEAA Application Form</h1>
              <button className="close-btn" onClick={onCancel}>×</button>
            </div>

            {!showReview && (
              <div className="application-progress">
                <div className="progress-steps">
                  {stepTitles.map((title, index) => (
                    <div key={index} className={`progress-step ${index + 1 === currentStep ? 'active' : ''} ${index + 1 < currentStep ? 'completed' : ''}`}>
                      <div className="step-number">{index + 1}</div>
                      <div className="step-title">{title}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="application-content">
              {showReview ? (
                renderReviewPage()
              ) : (
                <>
                  {currentStep === 1 && renderStep1()}
                  {currentStep === 2 && renderStep2()}
                  {currentStep === 3 && renderStep3()}
                  {currentStep === 4 && renderStep4()}
                  {currentStep === 5 && renderStep5()}
                  <div className="form-actions">
                    {currentStep > 1 && (
                      <button className="btn-previous" onClick={handlePrevious}>Previous</button>
                    )}
                    <button className="btn-next" onClick={handleNext}>
                      {currentStep === totalSteps ? 'Review Application' : 'Next'}
                    </button>
                  </div>
                </>
              )}
            </div>
          </>
        )}

        {showConfirmDialog && (
          <div className="confirm-dialog-overlay">
            <div className="confirm-dialog">
              <div className="confirm-icon">⚠️</div>
              <h3>Submit your application?</h3>
              <p>This will lock your application and you will no longer be able to edit it.</p>
              <div className="confirm-actions">
                <button className="btn-cancel" onClick={() => setShowConfirmDialog(false)}>Cancel</button>
                <button className="btn-confirm" onClick={handleSubmit}>Yes, submit</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FullApplicationForm;
