import { useEffect, useState } from 'react';
import type { StateResult } from '../api';
import { formatValue, outputParameters, OUTPUT_UNITS, PAIRS, PARAMETERS, type Inputs, type PairId } from '../model';
import Icon from './Icon';
import SectionHeading from './SectionHeading';

export type AcceptedCalculation = { result: StateResult; inputs: Inputs; pair: PairId };
const phaseTranslations: Record<string, string> = { 'Superheated vapor': 'بخار فوق‌گرم', 'Compressed liquid': 'مایع فشرده', 'Supercritical fluid': 'سیال فوق‌بحرانی', Gas: 'گاز', 'Two-phase mixture': 'مخلوط دوفازی', 'Liquid–vapor mixture':'مخلوط دوفازی', 'Saturated liquid':'مایع اشباع', 'Saturated vapor':'بخار اشباع' };

export default function ResultsPanel({ pair, accepted, busy }: { pair: PairId; accepted: AcceptedCalculation | null; busy: boolean }) {
  const result = accepted?.result ?? null;
  const [copyStatus,setCopyStatus] = useState('');
  useEffect(()=>setCopyStatus(''),[accepted]);
  async function copy() {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify({name:'termoyazd',inputs:result.normalized_inputs,properties:result.properties,units:result.units,quality:result.quality,phase:result.phase,region:result.region,saturation:result.saturation,solver:result.method,convergence:result.convergence,warnings:result.warnings},null,2));
      setCopyStatus('Copied (کپی شد)');
    } catch { setCopyStatus('Clipboard unavailable (دسترسی به کلیپ‌بورد ممکن نیست)'); }
  }
  const quality = result?.quality;
  const hasQuality = typeof quality === 'number' && Number.isFinite(quality) && quality >= 0 && quality <= 1;
  return <section className={`results-section ${busy ? 'is-loading' : ''}`} aria-label="Calculation results" aria-busy={busy}>
    <SectionHeading number="03" title="Calculated properties" fa="نتایج محاسبه" note={busy ? 'SOLVING STATE' : result ? 'CALCULATION COMPLETE' : 'AWAITING CALCULATION'}/>
    <div className="results-toolbar"><span className={`result-status ${result ? 'success' : ''}`}><i/>{busy ? 'Computing real-fluid properties…' : result ? 'Valid thermodynamic state' : 'No calculated state yet'}</span><button type="button" className="clear-button" disabled={!result || busy} onClick={copy}>Copy results (کپی نتایج)</button><span className="method-pill">IAPWS-IF97</span></div>
    <p role="status" className="micro">{copyStatus}</p><div className="property-grid">{outputParameters(pair).map(parameter => <article className="property-card" key={parameter} aria-label={`${PARAMETERS[parameter].name} result`}><div className="property-top"><span className="property-icon"><Icon name={PARAMETERS[parameter].icon} size={22}/></span><span className="property-symbol">{parameter}</span></div><h3>{PARAMETERS[parameter].name}</h3><p lang="fa" className="persian-label">{PARAMETERS[parameter].fa}</p><div className="property-number"><strong>{result ? formatValue(result.properties[parameter], parameter === 'v' ? 7 : parameter === 's' ? 6 : 4) : <span className={busy ? 'skeleton-number' : ''}>—</span>}</strong><span>{result?.units[parameter] ?? OUTPUT_UNITS[parameter]}</span></div><div className="property-foot">{result ? <><Icon name="check" size={12}/>Calculated by IF97</> : busy ? 'Calculating…' : 'Waiting for a real calculation'}</div></article>)}</div>
    <div className="state-summary panel"><div className="state-summary-header"><span><Icon name="layers" size={18}/>State information <small>(اطلاعات حالت)</small></span><span className="region-badge">{result ? `IF97 · Region ${result.region}` : 'IF97 · Region —'}</span></div><dl className="state-list"><div><dt>Phase <small>(فاز)</small></dt><dd>{result ? <>{result.phase}<small lang="fa">{phaseTranslations[result.phase] ?? ''}</small></> : '—'}</dd></div><div><dt>Steam quality <small>(کیفیت بخار)</small></dt><dd>{hasQuality ? <>{formatValue(quality, 5)} <span className="muted">kg/kg</span></> : result ? <span className="muted">Not defined <small>(تعریف نمی‌شود)</small></span> : '—'}</dd></div><div><dt>Temperature / pressure<small>(دما / فشار حالت)</small></dt><dd>{result ? <>{formatValue(result.properties.T, 3)} °C <span className="muted">/</span> {formatValue(result.properties.P, 3)} kPa</> : '—'}</dd></div>{result && Object.entries(result.saturation).map(([key,value])=><div key={key}><dt>{key==='temperature_at_P_c'?'Saturation temperature at P':'Saturation pressure at T'}<small>(مرز اشباع)</small></dt><dd>{formatValue(value,5)} {key==='temperature_at_P_c'?'°C':'kPa'}</dd></div>)}</dl><p className="state-note"><Icon name="info" size={14}/><span>{hasQuality ? 'Saturation state reported by IF97. دما و فشار بالا، مختص حالت اشباع گزارش‌شده هستند.' : result ? 'Quality is not defined for a single-phase state. کیفیت بخار در حالت تک‌فازی تعریف نمی‌شود.' : 'Phase, quality and saturation information appear only after a verified calculation. اطلاعات فاز و اشباع پس از محاسبه معتبر نمایش داده می‌شوند.'}</span></p></div>
    <div className="input-receipt"><div><Icon name="check" size={15}/><span>{accepted ? 'Inputs used in this calculation' : 'Calculation inputs'}<small lang="fa">ورودی‌های استفاده‌شده در محاسبه</small></span></div>{accepted ? PAIRS.find(p => p.id === accepted.pair)!.parameters.map((parameter, index) => <span className="receipt-value" key={parameter}><b>{parameter}</b>{accepted.inputs[index].value} <small>{accepted.inputs[index].unit}</small></span>) : <span className="muted">No submitted state · هنوز محاسبه‌ای انجام نشده</span>}</div>
  </section>;
}
