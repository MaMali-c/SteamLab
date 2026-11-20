import { PARAMETERS, type InputValue, type Parameter } from '../model';
import Icon from './Icon';
export default function ParameterInput({ parameter, input, onValue, onUnit }: { parameter: Parameter; input: InputValue; onValue: (value: string) => void; onUnit: (unit: string) => void }) {
  const definition = PARAMETERS[parameter];
  return <div className="parameter-field"><label htmlFor={`input-${parameter}`}><span className="input-icon"><Icon name={definition.icon}/></span><span>{definition.name} <b>({parameter})</b><small lang="fa">{definition.fa}</small></span></label><div className="input-control"><input id={`input-${parameter}`} type="number" step="any" inputMode="decimal" value={input.value} onChange={event => onValue(event.target.value)} placeholder="Enter value" aria-describedby={`hint-${parameter}`} autoComplete="off"/><select aria-label={`${definition.name} unit (${definition.fa})`} value={input.unit} onChange={event => onUnit(event.target.value)}>{definition.units.map(unit => <option key={unit.label} value={unit.label}>{unit.label}</option>)}</select></div><p className="field-hint" id={`hint-${parameter}`}>{definition.hint}</p></div>;
}
