import { useEffect, useRef, useState, type FormEvent } from 'react';
import Diagram from './Diagram';
import { request, validateResult } from './api';
import { changeUnit, initialInputs, normalizedValue, PAIRS, PARAMETERS, validateInputs, type Inputs, type PairId } from './model';
import Sidebar from './components/Sidebar';
import Icon from './components/Icon';
import SectionHeading from './components/SectionHeading';
import InputPairSelector from './components/InputPairSelector';
import ParameterInput from './components/ParameterInput';
import ResultsPanel, { type AcceptedCalculation } from './components/ResultsPanel';
import CalculationDetails from './components/CalculationDetails';
import StatusMessage from './components/StatusMessage';

export default function App() {
  const [pair, setPair] = useState<PairId>('TP');
  const [inputs, setInputs] = useState<Inputs>(() => initialInputs('TP', true));
  const [accepted, setAccepted] = useState<AcceptedCalculation | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [online, setOnline] = useState<boolean | null>(null);
  const pending = useRef<AbortController | null>(null);
  const selected = PAIRS.find(item => item.id === pair)!;

  useEffect(() => {
    const controller = new AbortController();
    request<{ app: string }>('/api/health', { signal: controller.signal })
      .then(value => { if (!controller.signal.aborted) setOnline(value.app === 'termoyazd'); })
      .catch(() => { if (!controller.signal.aborted) setOnline(false); });
    return () => { controller.abort(); pending.current?.abort(); };
  }, []);

  function invalidate() {
    pending.current?.abort(); pending.current = null;
    setAccepted(null); setError(''); setBusy(false);
  }
  function selectPair(value: PairId) {
    if (value === pair) return;
    invalidate(); setPair(value); setInputs(initialInputs(value));
  }
  function edit(index: number, value: string, unit = false) {
    invalidate();
    setInputs(current => current.map((input, at) => at !== index ? input : unit ? changeUnit(selected.parameters[index], input, value) : { ...input, value }) as Inputs);
  }
  function clear() { invalidate(); setInputs(initialInputs(pair)); }
  function example() { invalidate(); setPair('TP'); setInputs(initialInputs('TP', true)); }

  async function calculate(event: FormEvent) {
    event.preventDefault(); invalidate();
    const invalid = validateInputs(pair, inputs);
    if (invalid) { setError(invalid); return; }
    const controller = new AbortController(); pending.current = controller; setBusy(true);
    try {
      const values = Object.fromEntries(selected.parameters.map((parameter,index)=>[parameter,normalizedValue(parameter,inputs[index])]));
      const raw = await request<unknown>('/api/calculate', { method:'POST', signal:controller.signal, headers:{'Content-Type':'application/json'}, body:JSON.stringify({input_pair:selected.parameters.join('_'),values}) });
      if (controller.signal.aborted) return;
      const result = validateResult(raw,pair,values);
      setAccepted({ result, inputs: inputs.map(input => ({ ...input })) as Inputs, pair });
      setOnline(true);
    } catch (failure) {
      if (!controller.signal.aborted) setError(failure instanceof TypeError ? 'Cannot reach the scientific engine. Please retry shortly. ارتباط با موتور علمی برقرار نیست؛ کمی بعد دوباره تلاش کنید.' : (failure as Error).message);
    } finally { if (pending.current === controller) { pending.current = null; setBusy(false); } }
  }

  return <div className="app-shell"><a className="skip-link" href="#calculator">Skip to calculator (رفتن به محاسبه‌گر)</a><Sidebar online={online}/><main>
    <header className="topbar"><div className="breadcrumb"><Icon name="calc" size={15}/><span>Engineering workspace</span><span className="slash">/</span><strong>Property Calculator</strong></div><span className="topbar-tag"><i/>PURE WATER ONLY</span></header>
    <section className="hero"><div><p className="eyebrow"><span/>WATER & STEAM PROPERTY CALCULATOR</p><h1>Every state.<br/><span>A clearer understanding.</span></h1><p className="hero-description">Define two properties. Explore your thermodynamic state.<span lang="fa" dir="rtl">دو خاصیت را مشخص کنید؛ حالت ترمودینامیکی را دقیق‌تر بشناسید.</span></p><div className="hero-tags"><span>Real-fluid formulation</span><span>SI engineering units</span><span>IAPWS-IF97</span></div></div><div className="hero-visual" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="hero-water"><Icon name="drop" size={110}/><span>H₂O</span></div><span className="orbit-label label-top">THERMODYNAMICS</span><span className="orbit-label label-bottom">PRECISION IN EVERY STATE</span></div></section>
    <section className="calculator-section" id="calculator"><SectionHeading number="01" title="Select input pair" fa="انتخاب جفت ورودی" note="11 INPUT COMBINATIONS"/><InputPairSelector selected={pair} onSelect={selectPair}/>
      <div className="workspace-grid"><div className="calculator-column"><section className="panel input-panel"><SectionHeading number="02" title="Enter values" fa="ورود مقادیر"/><form noValidate onSubmit={calculate}><div className="input-fields">{selected.parameters.map((parameter, index) => <ParameterInput key={parameter} parameter={parameter} input={inputs[index]} onValue={value => edit(index, value)} onUnit={unit => edit(index, unit, true)}/>)}</div><div className="form-footer"><span className="input-pair-note"><Icon name="info" size={14}/>{selected.available ? 'Pressure must be absolute (فشار مطلق)' : 'Form ready · Solver pending (حلگر هنوز متصل نیست)'}</span><div className="form-actions"><button type="button" className="clear-button" onClick={clear}><Icon name="reset" size={16}/>Clear <span>(پاک کردن)</span></button><button className="calculate-button" disabled={busy} type="submit">{busy ? <span className="spinner"/> : <Icon name="calc" size={18}/>}<span>{busy ? 'Calculating…' : 'Calculate'}<small lang="fa">{busy ? 'در حال محاسبه' : 'محاسبه خواص'}</small></span>{!busy && <Icon name="arrow" size={17}/>}</button></div></div></form></section>
        {!selected.available && <StatusMessage kind="info"><strong>Interface ready · Scientific solver pending</strong><p lang="fa" dir="rtl">فرم {PARAMETERS[selected.parameters[0]].fa} و {PARAMETERS[selected.parameters[1]].fa} آماده است. API فعلی فقط جفت دما و فشار را پشتیبانی می‌کند.</p></StatusMessage>}
        {error && <StatusMessage kind="error"><strong>Calculation could not complete <span>(محاسبه انجام نشد)</span></strong><p>{error}</p></StatusMessage>}
        <ResultsPanel pair={pair} accepted={accepted} busy={busy}/>
      </div><aside className="context-column"><section className="diagram-section" id="diagrams"><Diagram result={accepted?.result ?? null}/></section><section className="panel context-note"><span className="context-note-icon"><Icon name="info"/></span><div><h3>A map of your state <small>(نمایی از حالت)</small></h3><p>Saturation boundaries are computed by IF97. A state marker appears only when a successful calculation also certifies uniqueness.</p><p lang="fa" dir="rtl">مرزهای اشباع از موتور علمی دریافت می‌شوند؛ نقطه حالت فقط پس از محاسبه معتبر با یکتایی تأییدشده نمایش داده می‌شود.</p></div></section><div className="quick-example"><span>Try a starting point <small>(ورودی نمونه)</small></span><button type="button" onClick={example}>300 °C <i>/</i> 500 kPa <Icon name="arrow" size={15}/></button><p>Loads inputs only · فقط ورودی‌ها تنظیم می‌شوند</p></div></aside></div>
    </section>
    <CalculationDetails pair={pair} result={accepted?.result ?? null}/>
    <section className="sources-section panel" id="sources"><div className="sources-intro"><span className="source-icon"><Icon name="book" size={23}/></span><div><h2>Built on established science <small>(درباره پروژه و منابع)</small></h2><p>termoyazd is a pure-water thermodynamic workspace. Results come from the Python IAPWS-IF97 engine. Online mode runs Python in a separate browser worker; local mode uses FastAPI.</p><p lang="fa" dir="rtl">مقادیر از موتور علمی موجود دریافت می‌شوند. مقایسه عددی با جزوه تا بررسی مستقل داده‌های آن نمایش داده نمی‌شود.</p></div></div><div className="source-links"><a href="https://iapws.org/relguide/IF97-Rev.html" target="_blank" rel="noreferrer"><span>IAPWS-IF97 release<small>مرجع فرمول‌بندی صنعتی</small></span><Icon name="external" size={17}/></a><a href="https://iapws.readthedocs.io/en/stable/iapws.iapws97.html" target="_blank" rel="noreferrer"><span>Python iapws documentation<small>مستندات کتابخانه محاسباتی</small></span><Icon name="external" size={17}/></a></div></section>
    <section className="help-section" id="help"><div><p className="eyebrow">A LITTLE GUIDANCE</p><h2>Good inputs. Reliable interpretation.</h2><p lang="fa" dir="rtl">راهنمای استفاده از محاسبه‌گر</p></div><div className="help-questions"><details><summary>How do I calculate a state? <span>(چطور محاسبه کنم؟)</span></summary><p>Select T + P, enter temperature and absolute pressure, select their units, then Calculate. جفت دما و فشار را انتخاب کنید؛ مقدارها و واحدها را وارد کرده و محاسبه را بزنید.</p></details><details><summary>How are inverse pairs solved? <span>(جفت‌های معکوس چطور حل می‌شوند؟)</span></summary><p>All eleven pairs call the IF97 backend. Inverse calculations may report multiple solutions or numerical warnings. همه جفت‌ها به موتور علمی متصل هستند؛ پاسخ مبهم یا نامعتبر به‌صورت خطا نمایش داده می‌شود.</p></details><details><summary>Why did my previous result disappear? <span>(چرا نتیجه پاک شد؟)</span></summary><p>Editing an input, unit or pair clears the previous result so it cannot be mistaken for the new state. تغییر مقدار، واحد یا جفت ورودی، نتیجه قبلی را پاک می‌کند تا با حالت جدید اشتباه نشود.</p></details></div></section>
    <footer><a href="#calculator">termoyazd</a><span>Water & steam · Scientific clarity <small>(شفافیت در محاسبه علمی)</small></span><span>FRONTEND WORKSPACE · v0.1.0</span></footer>
  </main></div>;
}
