import React, { useState } from 'react';
import { sendApprovalEmail } from '../services/email/emailService';

interface Student {
  id: number;
  name: string;
  email: string;
  status: string;
}

/**
 * Example Admin Approval Component with Email Integration
 * This shows how to integrate EmailJS into your existing admin approval workflow
 */
const AdminApprovalWithEmail: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([
    {
      id: 1,
      name: 'Juan Dela Cruz',
      email: 'juan.delacruz@student.tcu.edu.ph',
      status: 'pending',
    },
    {
      id: 2,
      name: 'Maria Santos',
      email: 'maria.santos@student.tcu.edu.ph',
      status: 'pending',
    },
  ]);

  const [sendingEmail, setSendingEmail] = useState<number | null>(null);
  const [notification, setNotification] = useState<{
    type: 'success' | 'error';
    message: string;
  } | null>(null);

  /**
   * Handle student approval and send email
   */
  const handleApprove = async (student: Student) => {
    try {
      setSendingEmail(student.id);
      setNotification(null);

      // Step 1: Update student status in backend (your existing API call)
      // await axios.put(`/api/students/${student.id}/approve`);

      // Step 2: Send approval email
      const emailResult = await sendApprovalEmail(student.name, student.email);

      if (emailResult.success) {
        // Update local state
        setStudents((prev) =>
          prev.map((s) =>
            s.id === student.id ? { ...s, status: 'approved' } : s
          )
        );

        setNotification({
          type: 'success',
          message: `${student.name} has been approved and notified via email at ${student.email}`,
        });
      } else {
        setNotification({
          type: 'error',
          message: `Approved but failed to send email: ${emailResult.message}`,
        });
      }
    } catch (error: any) {
      setNotification({
        type: 'error',
        message: `Error approving student: ${error.message}`,
      });
    } finally {
      setSendingEmail(null);
    }
  };

  /**
   * Bulk approve multiple students
   */
  const handleBulkApprove = async () => {
    const pendingStudents = students.filter((s) => s.status === 'pending');

    if (pendingStudents.length === 0) {
      setNotification({
        type: 'error',
        message: 'No pending students to approve',
      });
      return;
    }

    setSendingEmail(-1); // Indicate bulk operation
    let successCount = 0;
    let failCount = 0;

    for (const student of pendingStudents) {
      try {
        // Approve in backend
        // await axios.put(`/api/students/${student.id}/approve`);

        // Send email
        const emailResult = await sendApprovalEmail(student.name, student.email);

        if (emailResult.success) {
          successCount++;
          setStudents((prev) =>
            prev.map((s) =>
              s.id === student.id ? { ...s, status: 'approved' } : s
            )
          );
        } else {
          failCount++;
        }
      } catch (error) {
        failCount++;
      }

      // Small delay to avoid rate limiting
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    setSendingEmail(null);
    setNotification({
      type: successCount > 0 ? 'success' : 'error',
      message: `Bulk approval complete: ${successCount} successful, ${failCount} failed`,
    });
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>TCU-CEAA Student Approvals</h1>
        <button
          onClick={handleBulkApprove}
          disabled={sendingEmail !== null}
          style={styles.bulkButton}
        >
          {sendingEmail === -1 ? 'Processing...' : 'Approve All & Send Emails'}
        </button>
      </div>

      {notification && (
        <div
          style={{
            ...styles.notification,
            ...(notification.type === 'success'
              ? styles.successNotification
              : styles.errorNotification),
          }}
        >
          <strong>{notification.type === 'success' ? '✓' : '✕'}</strong>
          <span>{notification.message}</span>
        </div>
      )}

      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Student Name</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Status</th>
              <th style={styles.th}>Action</th>
            </tr>
          </thead>
          <tbody>
            {students.map((student) => (
              <tr key={student.id} style={styles.tr}>
                <td style={styles.td}>{student.name}</td>
                <td style={styles.td}>{student.email}</td>
                <td style={styles.td}>
                  <span
                    style={{
                      ...styles.badge,
                      ...(student.status === 'approved'
                        ? styles.approvedBadge
                        : styles.pendingBadge),
                    }}
                  >
                    {student.status}
                  </span>
                </td>
                <td style={styles.td}>
                  {student.status === 'pending' ? (
                    <button
                      onClick={() => handleApprove(student)}
                      disabled={sendingEmail !== null}
                      style={styles.approveButton}
                    >
                      {sendingEmail === student.id
                        ? '📧 Sending...'
                        : 'Approve & Email'}
                    </button>
                  ) : (
                    <span style={styles.approvedText}>✓ Approved</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={styles.infoBox}>
        <h3>📧 Email Notification Info</h3>
        <p>
          When you approve a student, they will automatically receive the
          official TCU-CEAA approval email with:
        </p>
        <ul>
          <li>Congratulations message</li>
          <li>Next steps instructions</li>
          <li>Contact information for support</li>
        </ul>
        <p>
          <strong>Note:</strong> Make sure student emails are correct before
          approving.
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
  } as React.CSSProperties,
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  } as React.CSSProperties,
  bulkButton: {
    padding: '12px 24px',
    backgroundColor: '#0066cc',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  } as React.CSSProperties,
  notification: {
    padding: '12px 16px',
    borderRadius: '6px',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  } as React.CSSProperties,
  successNotification: {
    backgroundColor: '#d4edda',
    color: '#155724',
    border: '1px solid #c3e6cb',
  } as React.CSSProperties,
  errorNotification: {
    backgroundColor: '#f8d7da',
    color: '#721c24',
    border: '1px solid #f5c6cb',
  } as React.CSSProperties,
  tableContainer: {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    overflow: 'hidden',
  } as React.CSSProperties,
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  } as React.CSSProperties,
  th: {
    padding: '12px',
    textAlign: 'left',
    backgroundColor: '#f8f9fa',
    fontWeight: '600',
    borderBottom: '2px solid #dee2e6',
  } as React.CSSProperties,
  tr: {
    borderBottom: '1px solid #dee2e6',
  } as React.CSSProperties,
  td: {
    padding: '12px',
  } as React.CSSProperties,
  badge: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600',
    textTransform: 'uppercase',
  } as React.CSSProperties,
  approvedBadge: {
    backgroundColor: '#d4edda',
    color: '#155724',
  } as React.CSSProperties,
  pendingBadge: {
    backgroundColor: '#fff3cd',
    color: '#856404',
  } as React.CSSProperties,
  approveButton: {
    padding: '8px 16px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '13px',
    fontWeight: '600',
    cursor: 'pointer',
  } as React.CSSProperties,
  approvedText: {
    color: '#28a745',
    fontWeight: '600',
  } as React.CSSProperties,
  infoBox: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#e7f3ff',
    borderLeft: '4px solid #0066cc',
    borderRadius: '4px',
  } as React.CSSProperties,
};

export default AdminApprovalWithEmail;
