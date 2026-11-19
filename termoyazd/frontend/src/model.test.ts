import { describe, it, expect } from 'vitest';
import { changeUnit, initialInputs, normalizedValue, outputParameters, validateInputs, formatValue, PAIRS } from './model';

describe('engineering input presentation', () => {
  it('converts temperature, pressure, quality and specific properties', () => {
    expect(changeUnit('T', { value: '300', unit: '°C' }, 'K')).toEqual({ value: '573.15', unit: 'K' });
    expect(changeUnit('P', { value: '500', unit: 'kPa' }, 'bar')).toEqual({ value: '5', unit: 'bar' });
    expect(changeUnit('x', { value: '0.3', unit: 'kg/kg' }, '%')).toEqual({ value: '30', unit: '%' });
    expect(normalizedValue('h', { value: '2000000', unit: 'J/kg' })).toBe(2000);
    expect(normalizedValue('v', { value: '100', unit: 'L/kg' })).toBe(.1);
    expect(normalizedValue('s', { value: '7000', unit: 'J/(kg·K)' })).toBe(7);
  });
  it('keeps empty fields empty when changing units', () => {
    expect(changeUnit('T', { value: '', unit: '°C' }, 'K')).toEqual({ value: '', unit: 'K' });
  });
  it('validates quality, positive pressure and volume, and missing values', () => {
    expect(validateInputs('Tx', [{ value: '100', unit: '°C' }, { value: '101', unit: '%' }])).toMatch(/Quality/);
    expect(validateInputs('TP', [{ value: '300', unit: '°C' }, { value: '0', unit: 'bar' }])).toMatch(/positive/);
    expect(validateInputs('Tv', [{ value: '100', unit: '°C' }, { value: '-1', unit: 'm³/kg' }])).toMatch(/positive/);
    expect(validateInputs('TP', initialInputs('TP'))).toMatch(/finite/);
    expect(validateInputs('TP', initialInputs('TP', true))).toBeNull();
  });
  it('uses four output slots that exclude the chosen known properties', () => {
    expect(outputParameters('TP')).toEqual(['h', 'u', 's', 'v']);
    expect(outputParameters('Ts')).toEqual(['h', 'u', 'v', 'P']);
    expect(outputParameters('Ph')).toEqual(['u', 's', 'v', 'T']);
    for (const pair of PAIRS) {
      const outputs = outputParameters(pair.id);
      expect(outputs).toHaveLength(4);
      expect(outputs.some(parameter => pair.parameters.includes(parameter))).toBe(false);
    }
  });
  it('never rounds tiny positive values into a false zero', () => {
    expect(formatValue(1e-9)).toBe('1.00000e-9');
    expect(formatValue(Infinity)).toBe('—');
  });
});
