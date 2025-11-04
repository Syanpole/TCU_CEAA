import React, { useState } from 'react';
import './DocumentRequirements.css';

interface DocumentRequirementsProps {
  darkMode?: boolean;
  schoolYear?: string;
  semester?: string;
}

interface UploadedDocument {
  id: number;
  type: string;
  semester: string;
  schoolYear: string;
  files: File[];
  uploadDate: string;
}

const DocumentRequirements: React.FC<DocumentRequirementsProps> = ({ darkMode = false, schoolYear = 'S.Y 2025-2026', semester = '1ST SEMESTER' }) => {
  const [selectedSemester, setSelectedSemester] = useState(semester);
  const [selectedSchoolYear, setSelectedSchoolYear] = useState(schoolYear);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [documentType, setDocumentType] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  
  // Empty documents array - no sample data
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);

  const documentTypes = [
    '[A] Certificate of Matriculation for 1st Semester, S.Y. 2024-2025',
    '[B] Certificate of Grades - Last Semester',
    '[C] Junior High School Certificate/Grade 10 Report Card (New Applicant)',
    '[D] Senior High School Diploma/Grade 12 Report Card (New Applicant)',
    '[E] School ID or Valid Government-Issued ID',
    '[F] Parent\'s Voter Registration - Taguig City',
    '[G] Student\'s Voter Registration - Taguig City (18+ years old)',
    '[H] Birth Certificate (PSA/NSO/Civil Registry)',
    '[I] Form 137 - Elementary/High School',
    '[J] Certificate of Academic Excellence (Honors Scholars)'
  ];

  const handleAddRequirement = () => {
    setShowUploadModal(true);
    setDocumentType('');
    setSelectedFiles(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFiles(e.target.files);
    }
  };

  const handleUploadDocument = () => {
    if (!documentType || !selectedFiles || selectedFiles.length === 0) {
      alert('Please select document type and files to upload');
      return;
    }

    const newDocument: UploadedDocument = {
      id: Date.now(),
      type: documentType,
      semester: selectedSemester,
      schoolYear: selectedSchoolYear,
      files: Array.from(selectedFiles),
      uploadDate: new Date().toLocaleDateString()
    };

    setUploadedDocuments([...uploadedDocuments, newDocument]);
    setShowUploadModal(false);
    setDocumentType('');
    setSelectedFiles(null);
  };

  const handleCloseModal = () => {
    setShowUploadModal(false);
    setDocumentType('');
    setSelectedFiles(null);
  };

  const handleDeleteDocument = (docId: number) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      setUploadedDocuments(uploadedDocuments.filter(doc => doc.id !== docId));
    }
  };

  const handleViewDocument = (doc: UploadedDocument) => {
    // Handle viewing document - will open file preview
    console.log('View document:', doc);
    alert(`Viewing: ${doc.type}\nFiles: ${doc.files.length}\nUploaded: ${doc.uploadDate}`);
  };

  return (
    <div className={`document-requirements ${darkMode ? 'dark-theme' : 'light-theme'}`}>
      {/* Upload Modal */}
      {showUploadModal && (
        <div className="upload-modal-overlay" onClick={handleCloseModal}>
          <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Upload Document</h2>
              <button className="close-modal-btn" onClick={handleCloseModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Document Type <span className="required">*</span></label>
                <select 
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="document-type-select"
                >
                  <option value="">Select Document Type</option>
                  {documentTypes.map((type, index) => (
                    <option key={index} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Upload Files <span className="required">*</span></label>
                <div className="file-upload-area">
                  <input
                    type="file"
                    multiple
                    accept="image/*,.pdf"
                    onChange={handleFileChange}
                    className="file-input"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="file-upload-label">
                    <span className="upload-icon">📁</span>
                    <span className="upload-text">
                      {selectedFiles && selectedFiles.length > 0
                        ? `${selectedFiles.length} file(s) selected`
                        : 'Click to browse or drag files here'}
                    </span>
                    <span className="upload-hint">Supported: Images, PDF</span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Semester & School Year</label>
                <div className="info-display">
                  <span>📅 {selectedSemester}</span>
                  <span>•</span>
                  <span>{selectedSchoolYear}</span>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-cancel" onClick={handleCloseModal}>
                Cancel
              </button>
              <button className="btn-upload" onClick={handleUploadDocument}>
                Upload Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="requirements-header">
        <div className="header-left">
          <h1>Submission of Requirements</h1>
          <p className="header-subtitle">Upload and manage your scholarship documents</p>
        </div>
        
        <div className="header-right">
          <div className="filter-group">
            <label>Semester:</label>
            <select 
              className="semester-select"
              value={selectedSemester}
              onChange={(e) => setSelectedSemester(e.target.value)}
            >
              <option value="1ST SEMESTER">1st Semester</option>
              <option value="2ND SEMESTER">2nd Semester</option>
              <option value="SUMMER">Summer</option>
            </select>
          </div>

          <div className="filter-group">
            <label>School Year:</label>
            <select 
              className="school-year-select"
              value={selectedSchoolYear}
              onChange={(e) => setSelectedSchoolYear(e.target.value)}
            >
              <option value="S.Y 2025-2026">S.Y 2025-2026</option>
              <option value="S.Y 2024-2025">S.Y 2024-2025</option>
            </select>
          </div>

          <button className="add-requirement-btn" onClick={handleAddRequirement}>
            <span className="btn-icon">+</span>
            Add Document
          </button>
        </div>
      </div>

      <div className="documents-container">
        {uploadedDocuments.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📄</div>
            <h3>No Documents Uploaded Yet</h3>
            <p>Start by uploading your required documents for the scholarship application.</p>
            <button className="btn-upload-first" onClick={handleAddRequirement}>
              <span className="btn-icon">+</span>
              Upload Your First Document
            </button>
          </div>
        ) : (
          <div className="documents-grid">
            {uploadedDocuments.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="card-header">
                  <div className="document-icon">📎</div>
                  <button 
                    className="delete-btn"
                    onClick={() => handleDeleteDocument(doc.id)}
                    title="Delete document"
                  >
                    ×
                  </button>
                </div>
                
                <div className="card-body">
                  <h3 className="document-title">{doc.type}</h3>
                  
                  <div className="document-info">
                    <div className="info-item">
                      <span className="info-icon">📅</span>
                      <span className="info-text">{doc.semester}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-icon">📚</span>
                      <span className="info-text">{doc.schoolYear}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-icon">📁</span>
                      <span className="info-text">{doc.files.length} file(s)</span>
                    </div>
                    <div className="info-item">
                      <span className="info-icon">🕒</span>
                      <span className="info-text">Uploaded: {doc.uploadDate}</span>
                    </div>
                  </div>
                </div>

                <div className="card-footer">
                  <button 
                    className="btn-view-document"
                    onClick={() => handleViewDocument(doc)}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentRequirements;
