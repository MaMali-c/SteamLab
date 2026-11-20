export type Parameter = 'T' | 'P' | 'x' | 's' | 'u' | 'h' | 'v';
export type PairId = 'TP' | 'Tx' | 'Px' | 'Ts' | 'Tu' | 'Th' | 'Tv' | 'Ps' | 'Pu' | 'Ph' | 'Pv';
export type InputValue = { value: string; unit: string };
export type Inputs = [InputValue, InputValue];
type Unit = { label: string; factor: number; offset?: number };
export type ParameterDefinition = { name: string; fa: string; symbol: string; icon: string; units: Unit[]; hint: string };
export const PARAMETERS: Record<Parameter, ParameterDefinition> = {
  T: { name: 'Temperature', fa: 'دما', symbol: 'T', icon: 'temp', units: [{ label: '°C', factor: 1 }, { label: 'K', factor: 1, offset: -273.15 }], hint: 'Thermodynamic temperature · دمای ترمودینامیکی' },
  P: { name: 'Pressure', fa: 'فشار', symbol: 'P', icon: 'pressure', units: [{ label: 'kPa', factor: 1 }, { label: 'MPa', factor: 1000 }, { label: 'bar', factor: 100 }], hint: 'Absolute pressure, not gauge pressure · فشار مطلق، نه فشار گیج' },
  x: { name: 'Steam quality', fa: 'کیفیت بخار', symbol: 'x', icon: 'drop', units: [{ label: 'kg/kg', factor: 1 }, { label: '%', factor: .01 }], hint: 'Vapor mass fraction, 0–1 or 0–100% · کسر جرمی بخار' },
  s: { name: 'Specific entropy', fa: 'آنتروپی ویژه', symbol: 's', icon: 'entropy', units: [{ label: 'kJ/(kg·K)', factor: 1 }, { label: 'J/(kg·K)', factor: .001 }], hint: 'Specific entropy · آنتروپی بر واحد جرم' },
  u: { name: 'Internal energy', fa: 'انرژی داخلی ویژه', symbol: 'u', icon: 'energy', units: [{ label: 'kJ/kg', factor: 1 }, { label: 'J/kg', factor: .001 }], hint: 'Specific internal energy · انرژی داخلی بر واحد جرم' },
  h: { name: 'Specific enthalpy', fa: 'آنتالپی ویژه', symbol: 'h', icon: 'layers', units: [{ label: 'kJ/kg', factor: 1 }, { label: 'J/kg', factor: .001 }], hint: 'Specific enthalpy · آنتالپی بر واحد جرم' },
  v: { name: 'Specific volume', fa: 'حجم ویژه', symbol: 'v', icon: 'box', units: [{ label: 'm³/kg', factor: 1 }, { label: 'L/kg', factor: .001 }], hint: 'Volume per unit mass; must be positive · حجم بر واحد جرم، مقدار مثبت' },
};
export const PAIRS: { id: PairId; parameters: [Parameter, Parameter]; available: boolean }[] = [
  { id: 'TP', parameters: ['T', 'P'], available: true },
  { id: 'Tx', parameters: ['T', 'x'], available: true },
  { id: 'Px', parameters: ['P', 'x'], available: true },
  { id: 'Ts', parameters: ['T', 's'], available: true },
  { id: 'Tu', parameters: ['T', 'u'], available: true },
  { id: 'Th', parameters: ['T', 'h'], available: true },
  { id: 'Tv', parameters: ['T', 'v'], available: true },
  { id: 'Ps', parameters: ['P', 's'], available: true },
  { id: 'Pu', parameters: ['P', 'u'], available: true },
  { id: 'Ph', parameters: ['P', 'h'], available: true },
  { id: 'Pv', parameters: ['P', 'v'], available: true },
];
export function initialInputs(pair: PairId, example = false): Inputs {
  const definition = PAIRS.find(item => item.id === pair)!;
  return definition.parameters.map(parameter => ({ value: example && parameter === 'T' ? '300' : example && parameter === 'P' ? '500' : '', unit: PARAMETERS[parameter].units[0].label })) as Inputs;
}
export function normalizedValue(parameter: Parameter, input: InputValue): number {
  const unit = PARAMETERS[parameter].units.find(unit => unit.label === input.unit);
  if (!unit) throw new Error('Unsupported engineering unit. واحد انتخاب‌شده معتبر نیست.');
  return Number(input.value) * unit.factor + (unit.offset ?? 0);
}
export function changeUnit(parameter: Parameter, input: InputValue, label: string): InputValue {
  if (!input.value.trim()) return { value: '', unit: label };
  const unit = PARAMETERS[parameter].units.find(unit => unit.label === label)!;
  const value = (normalizedValue(parameter, input) - (unit.offset ?? 0)) / unit.factor;
  return { value: Number.isFinite(value) ? String(Number(value.toPrecision(12))) : input.value, unit: label };
}
export function validateInputs(pair: PairId, inputs: Inputs): string | null {
  const parameters = PAIRS.find(item => item.id === pair)!.parameters;
  for (const [index, parameter] of parameters.entries()) {
    if (!inputs[index].value.trim() || !Number.isFinite(Number(inputs[index].value))) return `Enter a finite value for ${PARAMETERS[parameter].name}. مقدار عددی معتبر برای ${PARAMETERS[parameter].fa} وارد کنید.`;
    const value = normalizedValue(parameter, inputs[index]);
    if (!Number.isFinite(value)) return 'The entered value is too large. مقدار واردشده بیش از حد بزرگ است.';
    if ((parameter === 'P' || parameter === 'v') && value <= 0) return `${PARAMETERS[parameter].name} must be positive. ${PARAMETERS[parameter].fa} باید مثبت باشد.`;
    if (parameter === 'x' && (value < 0 || value > 1)) return 'Quality must be between 0 and 1 (0–100%). کیفیت بخار باید بین صفر و یک باشد.';
  }
  return null;
}
export function outputParameters(pair: PairId): Exclude<Parameter, 'x'>[] {
  const inputs = PAIRS.find(item => item.id === pair)!.parameters;
  return (['h', 'u', 's', 'v', 'T', 'P'] as const).filter(parameter => !inputs.includes(parameter)).slice(0, 4);
}
export const OUTPUT_UNITS = { T: '°C', P: 'kPa', h: 'kJ/kg', u: 'kJ/kg', s: 'kJ/(kg·K)', v: 'm³/kg' };
export function formatValue(value: number, maximumFractionDigits = 5): string {
  if (!Number.isFinite(value)) return '—';
  if (value !== 0 && (Math.abs(value) < .00001 || Math.abs(value) >= 1e8)) return value.toExponential(5);
  return value.toLocaleString('en-US', { maximumFractionDigits, minimumFractionDigits: 2 });
}
