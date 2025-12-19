import { isValidNumber, safeNumber, safeToFixed, safePercentage } from '../../utils/numberUtils';

describe('numberUtils - Additional Tests', () => {
  describe('Edge Cases', () => {
    it('should handle negative numbers', () => {
      expect(safeNumber(-42)).toBe(-42);
      expect(safeToFixed(-3.14159, 2)).toBe('-3.14');
    });

    it('should handle zero', () => {
      expect(isValidNumber(0)).toBe(true);
      expect(safeNumber(0)).toBe(0);
      expect(safeToFixed(0)).toBe('0.00');
    });

    it('should handle very large numbers', () => {
      expect(safeNumber(999999999)).toBe(999999999);
      expect(safeToFixed(999999999, 2)).toBe('999999999.00');
    });

    it('should handle very small decimals', () => {
      expect(safeToFixed(0.00001, 5)).toBe('0.00001');
    });
  });

  describe('String Conversions', () => {
    it('should handle string with whitespace', () => {
      expect(safeNumber('  42  ')).toBe(42);
      expect(safeToFixed('  3.14  ', 1)).toBe('3.1');
    });

    it('should handle empty strings', () => {
      expect(safeNumber('')).toBe(0);
      expect(safeToFixed('', 2)).toBe('0.00'); // Empty string converts to 0
    });
  });

  describe('Percentage Formatting', () => {
    it('should format whole numbers as percentages', () => {
      expect(safePercentage(100)).toBe('100.00%');
    });

    it('should format decimals as percentages', () => {
      expect(safePercentage(85.5)).toBe('85.50%');
    });

    it('should handle zero percentage', () => {
      expect(safePercentage(0)).toBe('0.00%');
    });
  });

  describe('Invalid Inputs', () => {
    it('should reject Infinity', () => {
      expect(isValidNumber(Infinity)).toBe(false);
      expect(isValidNumber(-Infinity)).toBe(false);
    });

    it('should reject special characters', () => {
      expect(isValidNumber('abc')).toBe(false);
      expect(isValidNumber('12@34')).toBe(false);
    });

    it('should handle mixed valid/invalid strings', () => {
      // safeNumber uses Number() which returns NaN for '123abc', then falls back to 0
      expect(safeNumber('123abc', 99)).toBe(99);
    });
  });
});
