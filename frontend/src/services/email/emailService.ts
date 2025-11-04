import emailjs from '@emailjs/browser';

emailjs.init(process.env.REACT_APP_EMAILJS_PUBLIC_KEY || '');

export interface EmailParams {
  to_name: string;
  to_email: string;
  student_name?: string;
  application_id?: string;
  application_type?: string;
  amount?: string;
  submission_date?: string;
  message?: string;
  [key: string]: any;
}

export const sendApplicationConfirmationEmail = async (
  studentName: string,
  studentEmail: string,
  applicationId: string = 'Pending Assignment',
  applicationType: string = 'Educational Assistance',
  amount: string = '5,000.00'
): Promise<{ success: boolean; message: string }> => {
  try {
    if (!studentName || !studentEmail) {
      throw new Error('Student name and email are required');
    }

    const submissionDate = new Date().toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });

    const templateParams = {
      to_name: studentName,
      to_email: studentEmail,
      student_name: studentName,
      application_id: applicationId,
      application_type: applicationType,
      amount: amount,
      submission_date: submissionDate,
      reply_to: 'ceaainfo@tcu.edu.ph',
      from_name: 'TCU-CEAA Scholarship Office',
    };

    console.log('Sending confirmation email to:', studentEmail);

    const response = await emailjs.send(
      process.env.REACT_APP_EMAILJS_SERVICE_ID || '',
      process.env.REACT_APP_EMAILJS_TEMPLATE_ID || '',
      templateParams
    );

    if (response.status === 200) {
      return { success: true, message: 'Confirmation email sent successfully!' };
    } else {
      throw new Error('Failed to send email');
    }
  } catch (error: any) {
    console.error('EmailJS Error:', error);
    return { success: false, message: error.text || error.message || 'Failed to send confirmation email.' };
  }
};

export const sendApprovalEmail = sendApplicationConfirmationEmail;

export const sendCustomEmail = async (
  params: EmailParams
): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await emailjs.send(
      process.env.REACT_APP_EMAILJS_SERVICE_ID || '',
      process.env.REACT_APP_EMAILJS_TEMPLATE_ID || '',
      params
    );

    if (response.status === 200) {
      return { success: true, message: 'Email sent successfully!' };
    } else {
      throw new Error('Failed to send email');
    }
  } catch (error: any) {
    console.error('EmailJS Error:', error);
    return { success: false, message: error.text || error.message || 'Failed to send email.' };
  }
};

const emailService = { sendApplicationConfirmationEmail, sendApprovalEmail, sendCustomEmail };
export default emailService;
