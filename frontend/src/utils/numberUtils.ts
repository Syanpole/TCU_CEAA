/**
 * Utility functions for safe number operations
 */

/**
 * Safely converts a value to a number and applies toFixed
 * @param value - The value to convert and format
 * @param decimals - Number of decimal places (default: 2)
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Formatted number string
 */
export const safeToFixed = (
  value: any, 
  decimals: number = 2, 
  fallback: number = 0
): string => {
  const numValue = Number(value);
  const safeValue = isNaN(numValue) ? fallback : numValue;
  return safeValue.toFixed(decimals);
};

/**
 * Safely converts a value to a number
 * @param value - The value to convert
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Safe number value
 */
export const safeNumber = (value: any, fallback: number = 0): number => {
  const numValue = Number(value);
  return isNaN(numValue) ? fallback : numValue;
};

/**
 * Formats a percentage value safely
 * @param value - The percentage value
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted percentage string
 */
export const safePercentage = (value: any, decimals: number = 2): string => {
  return `${safeToFixed(value, decimals)}%`;
};

/**
 * Validates if a value is a valid number
 * @param value - The value to validate
 * @returns Boolean indicating if value is a valid number
 */
export const isValidNumber = (value: any): boolean => {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  const numValue = Number(value);
  return !isNaN(numValue) && isFinite(numValue);
};

/**
 * Formats a number as currency (Philippine Peso)
 * @param value - The value to format
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Formatted currency string
 */
export const formatCurrency = (value: any, fallback: number = 0): string => {
  const numValue = safeNumber(value, fallback);
  return `₱${numValue.toLocaleString('en-PH', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
};

/**
 * Formats a number with proper thousands separators
 * @param value - The value to format
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Formatted number string
 */
export const formatNumber = (value: any, fallback: number = 0): string => {
  const numValue = safeNumber(value, fallback);
  return numValue.toLocaleString('en-PH');
};
