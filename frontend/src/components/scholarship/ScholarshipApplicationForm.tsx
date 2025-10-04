import React from 'react';

interface StudentInfo {
  studentId: string;
  studentName: string;
  yearLevel: string;
  program: string;
}

interface ScholarshipApplicationFormProps {
  studentInfo: StudentInfo;
  onComplete: () => void;
  onCancel: () => void;
}

const ScholarshipApplicationForm: React.FC<ScholarshipApplicationFormProps> = ({
  studentInfo,
  onComplete,
  onCancel
}) => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>Scholarship Application Form</h2>
      <p>Coming Soon...</p>
      <p>Student: {studentInfo.studentName}</p>
      <p>Student ID: {studentInfo.studentId}</p>
      <p>This feature is currently under development.</p>
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={onCancel}
          style={{
            padding: '10px 20px',
            marginRight: '10px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Back
        </button>
        <button 
          onClick={onComplete}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Complete
        </button>
      </div>
    </div>
  );
};

export default ScholarshipApplicationForm;