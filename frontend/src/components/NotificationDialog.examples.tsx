/**
 * NotificationDialog Usage Examples
 * 
 * This file demonstrates how to use the NotificationDialog component
 * and useNotification hook in your React components.
 */

import React from 'react';
import NotificationDialog from './NotificationDialog';
import { useNotification } from '../hooks/useNotification';

// ============================================
// METHOD 1: Using the NotificationDialog component directly
// ============================================

const DirectUsageExample: React.FC = () => {
  const [showDialog, setShowDialog] = React.useState(false);

  const handleDelete = () => {
    setShowDialog(true);
  };

  const confirmDelete = () => {
    console.log('Item deleted');
    setShowDialog(false);
    // Perform delete action here
  };

  const cancelDelete = () => {
    console.log('Delete cancelled');
    setShowDialog(false);
  };

  return (
    <div>
      <button onClick={handleDelete}>Delete Document</button>
      
      <NotificationDialog
        isOpen={showDialog}
        title="localhost:3004 says"
        message="Are you sure you want to delete this document? This action cannot be undone."
        type="warning"
        confirmText="OK"
        cancelText="Cancel"
        showCancel={true}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </div>
  );
};

// ============================================
// METHOD 2: Using the useNotification hook (Recommended)
// ============================================

const HookUsageExample: React.FC = () => {
  const { notification, confirm, alert } = useNotification();

  const handleDelete = async () => {
    const confirmed = await confirm({
      title: 'localhost:3004 says',
      message: 'Are you sure you want to delete this document? This action cannot be undone.',
      type: 'warning',
      confirmText: 'OK',
      cancelText: 'Cancel'
    });

    if (confirmed) {
      console.log('User confirmed deletion');
      // Perform delete action
    } else {
      console.log('User cancelled');
    }
  };

  const showSuccessAlert = async () => {
    await alert({
      title: 'Success',
      message: 'Your changes have been saved successfully!',
      type: 'success',
      confirmText: 'OK'
    });
    console.log('Alert dismissed');
  };

  const showErrorAlert = async () => {
    await alert({
      title: 'Error',
      message: 'Failed to save changes. Please try again.',
      type: 'error',
      confirmText: 'OK'
    });
  };

  return (
    <div>
      <button onClick={handleDelete}>Delete Document</button>
      <button onClick={showSuccessAlert}>Show Success</button>
      <button onClick={showErrorAlert}>Show Error</button>
      
      {/* Render the notification dialog */}
      <NotificationDialog {...notification} />
    </div>
  );
};

// ============================================
// EXAMPLE 3: Different notification types
// ============================================

const NotificationTypesExample: React.FC = () => {
  const { notification, confirm, alert } = useNotification();

  const showInfo = () => {
    alert({
      title: 'Information',
      message: 'This is an informational message.',
      type: 'info',
      confirmText: 'Got it'
    });
  };

  const showWarning = () => {
    confirm({
      title: 'Warning',
      message: 'This action requires confirmation.',
      type: 'warning',
      confirmText: 'Proceed',
      cancelText: 'Cancel'
    });
  };

  const showError = () => {
    alert({
      title: 'Error',
      message: 'An error occurred while processing your request.',
      type: 'error',
      confirmText: 'OK'
    });
  };

  const showSuccess = () => {
    alert({
      title: 'Success',
      message: 'Operation completed successfully!',
      type: 'success',
      confirmText: 'Great'
    });
  };

  return (
    <div style={{ display: 'flex', gap: '10px' }}>
      <button onClick={showInfo}>Info</button>
      <button onClick={showWarning}>Warning</button>
      <button onClick={showError}>Error</button>
      <button onClick={showSuccess}>Success</button>
      
      <NotificationDialog {...notification} />
    </div>
  );
};

// ============================================
// EXAMPLE 4: With custom callbacks
// ============================================

const CustomCallbacksExample: React.FC = () => {
  const { notification, confirm } = useNotification();

  const handleLogout = async () => {
    const confirmed = await confirm({
      title: 'Confirm Logout',
      message: 'Are you sure you want to logout? Any unsaved changes will be lost.',
      type: 'warning',
      confirmText: 'Logout',
      cancelText: 'Stay',
      onConfirm: () => {
        console.log('Logging out...');
        // Perform logout logic
      },
      onCancel: () => {
        console.log('User stayed logged in');
      }
    });

    console.log('Confirmation result:', confirmed);
  };

  return (
    <div>
      <button onClick={handleLogout}>Logout</button>
      <NotificationDialog {...notification} />
    </div>
  );
};

// ============================================
// EXAMPLE 5: Real-world usage in a component
// ============================================

const DocumentManagement: React.FC = () => {
  const { notification, confirm, alert } = useNotification();
  const [documents, setDocuments] = React.useState([
    { id: 1, name: 'Document 1.pdf' },
    { id: 2, name: 'Document 2.pdf' }
  ]);

  const deleteDocument = async (docId: number, docName: string) => {
    const confirmed = await confirm({
      title: 'localhost:3004 says',
      message: `Are you sure you want to delete "${docName}"? This action cannot be undone.`,
      type: 'warning',
      confirmText: 'OK',
      cancelText: 'Cancel'
    });

    if (confirmed) {
      // Simulate API call
      try {
        setDocuments(docs => docs.filter(d => d.id !== docId));
        await alert({
          title: 'Success',
          message: 'Document deleted successfully.',
          type: 'success',
          confirmText: 'OK'
        });
      } catch (error) {
        await alert({
          title: 'Error',
          message: 'Failed to delete document. Please try again.',
          type: 'error',
          confirmText: 'OK'
        });
      }
    }
  };

  return (
    <div>
      <h2>Documents</h2>
      {documents.map(doc => (
        <div key={doc.id} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <span>{doc.name}</span>
          <button onClick={() => deleteDocument(doc.id, doc.name)}>Delete</button>
        </div>
      ))}
      <NotificationDialog {...notification} />
    </div>
  );
};

// Export examples for documentation
export {
  DirectUsageExample,
  HookUsageExample,
  NotificationTypesExample,
  CustomCallbacksExample,
  DocumentManagement
};
