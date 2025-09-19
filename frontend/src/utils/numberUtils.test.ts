import { safeToFixed, safeNumber, safePercentage, isValidNumber } from './numberUtils';

describe('numberUtils', () => {
  describe('safeToFixed', () => {
    it('should handle valid numbers', () => {
      expect(safeToFixed(3.14159, 2)).toBe('3.14');
      expect(safeToFixed(100, 0)).toBe('100');
    });

    it('should handle string numbers', () => {
      expect(safeToFixed('3.14159', 2)).toBe('3.14');
      expect(safeToFixed('100')).toBe('100.00');
    });

    it('should handle invalid values with fallback', () => {
      expect(safeToFixed(null)).toBe('0.00');
      expect(safeToFixed(undefined)).toBe('0.00');
      expect(safeToFixed('invalid', 2, 99)).toBe('99.00');
      expect(safeToFixed(NaN)).toBe('0.00');
    });
  });

  describe('safeNumber', () => {
    it('should convert valid values to numbers', () => {
      expect(safeNumber(42)).toBe(42);
      expect(safeNumber('42')).toBe(42);
      expect(safeNumber('3.14')).toBe(3.14);
    });

    it('should return fallback for invalid values', () => {
      expect(safeNumber(null)).toBe(0);
      expect(safeNumber(undefined)).toBe(0);
      expect(safeNumber('invalid', 99)).toBe(99);
      expect(safeNumber(NaN)).toBe(0);
    });
  });

  describe('safePercentage', () => {
    it('should format percentages correctly', () => {
      expect(safePercentage(85.67)).toBe('85.67%');
      expect(safePercentage('90.5')).toBe('90.50%');
      expect(safePercentage(null)).toBe('0.00%');
    });
  });

  describe('isValidNumber', () => {
    it('should validate numbers correctly', () => {
      expect(isValidNumber(42)).toBe(true);
      expect(isValidNumber('42')).toBe(true);
      expect(isValidNumber('3.14')).toBe(true);
      expect(isValidNumber(0)).toBe(true);
      
      expect(isValidNumber(null)).toBe(false);
      expect(isValidNumber(undefined)).toBe(false);
      expect(isValidNumber('invalid')).toBe(false);
      expect(isValidNumber(NaN)).toBe(false);
      expect(isValidNumber(Infinity)).toBe(false);
    });
  });
});
