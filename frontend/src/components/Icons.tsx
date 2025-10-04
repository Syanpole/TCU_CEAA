import React from 'react';
import './Icons.css';

interface IconProps {
  size?: number;
  className?: string;
}

export const DashboardIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon dashboard-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
    </svg>
  </div>
);

export const DocumentIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon document-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
    </svg>
  </div>
);

export const GradeIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon grade-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,3L1,9L12,15L21,10.09V17H23V9M5,13.18V17.18L12,21L19,17.18V13.18L12,17L5,13.18Z"/>
    </svg>
  </div>
);

export const ApplicationIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon application-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M9,5V9H15V5H9M12,2A5,5 0 0,1 17,7A5,5 0 0,1 12,12A5,5 0 0,1 7,7A5,5 0 0,1 12,2M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"/>
    </svg>
  </div>
);

export const RequirementsIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon requirements-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M19,3H5C3.9,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.9 20.1,3 19,3M19,19H5V5H19V19M17,12H7V10H17V12M15,16H7V14H15V16M17,8H7V6H17V8Z"/>
    </svg>
  </div>
);

export const SettingsIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon settings-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z"/>
    </svg>
  </div>
);

export const MoneyIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon money-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M7,15H9C9,16.08 10.37,17 12,17C13.63,17 15,16.08 15,15C15,13.9 13.96,13.5 11.76,12.97C9.64,12.44 7,11.78 7,9C7,7.21 8.47,5.69 10.5,5.18V3H13.5V5.18C15.53,5.69 17,7.21 17,9H15C15,7.92 13.63,7 12,7C10.37,7 9,7.92 9,9C9,10.1 10.04,10.5 12.24,11.03C14.36,11.56 17,12.22 17,15C17,16.79 15.53,18.31 13.5,18.82V21H10.5V18.82C8.47,18.31 7,16.79 7,15Z"/>
    </svg>
  </div>
);

export const StudentIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon student-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M16,8A8,8 0 0,1 8,16H16M16,16A8,8 0 0,1 8,8V16M8,8A8,8 0 0,1 16,16V8"/>
    </svg>
  </div>
);

export const EmailIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon email-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M20,8L12,13L4,8V6L12,11L20,6M20,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V6C22,4.89 21.1,4 20,4Z"/>
    </svg>
  </div>
);

export const UploadIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon upload-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
    </svg>
  </div>
);

export const CheckIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon check-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/>
    </svg>
  </div>
);

export const ChartIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon chart-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M22,21H2V3H4V19H6V17H10V19H12V16H16V19H18V17H22V21Z"/>
    </svg>
  </div>
);

export const WarningIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon warning-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M13,14H11V10H13M13,18H11V16H13M1,21H23L12,2L1,21Z"/>
    </svg>
  </div>
);

export const InfoIcon: React.FC<IconProps> = ({ size = 20, className = '' }) => (
  <div className={`icon info-icon ${className}`} style={{ width: size, height: size }}>
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
    </svg>
  </div>
);