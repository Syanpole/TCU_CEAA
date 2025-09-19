/**
 * Utility functions for safe number operations
 */

/**
 * Safely converts a value to a fixed decimal number
 * @param value - The value to convert (can be number, string, null, or undefined)
 * @param decimals - Number of decimal places (default: 2)
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns String representation with fixed decimal places
 */
export const safeToFixed = (
  value: number | string | null | undefined | any, 
  decimals: number = 2, 
  fallback: number = 0
): string => {
  if (value === null || value === undefined || value === '') {
    return fallback.toFixed(decimals);
  }
  
  const numValue = typeof value === 'string' ? parseFloat(value) : Number(value);
  const safeValue = isNaN(numValue) ? fallback : numValue;
  return safeValue.toFixed(decimals);
};

/**
 * Safely converts a value to a number
 * @param value - The value to convert
 * @param defaultValue - Default value if conversion fails (default: 0)
 * @returns Numeric value or default
 */
export const safeToNumber = (value: any, defaultValue: number = 0): number => {
  if (value === null || value === undefined || value === '') {
    return defaultValue;
  }
  
  const numValue = typeof value === 'string' ? parseFloat(value) : Number(value);
  return isNaN(numValue) ? defaultValue : numValue;
};

// Alias for backward compatibility
export const safeNumber = safeToNumber;

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
 * Formats a number as currency with Philippine Peso symbol
 * @param amount - The amount to format
 * @param currency - Currency symbol (default: '₱')
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Formatted currency string
 */
export const formatCurrency = (amount: number | string | any, currency: string = '₱', fallback: number = 0): string => {
  const numAmount = safeToNumber(amount, fallback);
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numAmount).replace('$', currency);
};

/**
 * Formats a number with thousand separators
 * @param value - The number to format
 * @param decimals - Number of decimal places (default: 2)
 * @param fallback - Fallback value if conversion fails (default: 0)
 * @returns Formatted number string
 */
export const formatNumber = (value: number | string | any, decimals: number = 2, fallback: number = 0): string => {
  const numValue = safeToNumber(value, fallback);
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(numValue);
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
 * Calculates percentage with safe division
 * @param numerator - The numerator value
 * @param denominator - The denominator value
 * @param decimals - Number of decimal places (default: 1)
 * @returns Percentage as string with % symbol
 */
export const calculatePercentage = (numerator: number | string, denominator: number | string, decimals: number = 1): string => {
  const num = safeToNumber(numerator, 0);
  const den = safeToNumber(denominator, 0);
  
  if (den === 0) {
    return '0%';
  }
  
  const percentage = (num / den) * 100;
  return `${percentage.toFixed(decimals)}%`;
};
