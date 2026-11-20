import { useEffect, useRef, useState } from 'react';
import type { StateResult } from './api';
import { loadSaturation, type SaturationData } from './plotting/data';
import { buildDiagram, markerAllowed, type DiagramKind } from './plotting/specification';
import Icon from './components/Icon';
type Plotly = typeof import('plotly.js-basic-dist-min')['default'];
export default function Diagram({result}:{result:StateResult|null}){
  const [kind,setKind]=useState<DiagramKind>('Ts');
  const [data,setData]=useState<SaturationData|null>(null);
  const [error,setError]=useState('');
  const [actionError,setActionError]=useState('');
  const [ready,setReady]=useState(false);
  const [attempt,setAttempt]=useState(0);
  const host=useRef<HTMLDivElement>(null);
  const graph=useRef<{node:HTMLDivElement;plotly:Plotly}|null>(null);
  useEffect(()=>{let cancelled=false;setError('');loadSaturation().then(d=>{if(!cancelled)setData(d);}).catch(e=>{if(!cancelled)setError(e.message);});return()=>{cancelled=true;};},[attempt]);
  useEffect(()=>{
    if(!data||!host.current)return;
    let cancelled=false,observer:ResizeObserver|undefined,library:Plotly|undefined;
    const node=document.createElement('div'); node.style.width='100%';host.current.appendChild(node);
    setReady(false);setActionError('');setError('');graph.current=null;
    import('plotly.js-basic-dist-min').then(async module=>{
      if(cancelled)return;
      library=module.default;
      const spec=buildDiagram(kind,data,result);
      await library.react(node,spec.traces,spec.layout,spec.config);
      if(cancelled){library.purge(node);return;}
      graph.current={node,plotly:library};setReady(true);
      if(typeof ResizeObserver!=='undefined'){
        observer=new ResizeObserver(()=>{if(!cancelled)void library!.Plots.resize(node).catch(()=>{});});observer.observe(node);
      }
    }).catch(e=>{if(!cancelled)setError('Chart unavailable (نمودار در دسترس نیست): '+e.message);});
    return()=>{cancelled=true;observer?.disconnect();if(graph.current?.node===node)graph.current=null;library?.purge(node);node.remove();};
  },[kind,data,result,attempt]);
  async function control(action:'zoom'|'pan'|'reset'|'export'){
    const current=graph.current;if(!current)return;
    setActionError('');
    try{
      if(action==='export')await current.plotly.downloadImage(current.node,{format:'png',filename:`termoyazd-${kind}`,width:1400,height:1000,scale:2});
      else await current.plotly.relayout(current.node,action==='reset'?{'xaxis.autorange':true,'yaxis.autorange':true}:{dragmode:action});
    }catch{setActionError('Action failed. Please retry. اجرای فرمان ناموفق بود.');}
  }
  return <section className="panel diagram-panel" aria-label="Interactive thermodynamic diagrams"><div className="diagram-heading"><span>Scientific diagrams<small>(نمودارهای ترمودینامیکی)</small></span><span className="tag">IF97</span></div>
    <div className="diagram-tabs" role="group" aria-label="Diagram selection">{(['Ts','Pv','Ph'] as const).map(k=><button type="button" key={k} aria-pressed={kind===k} onClick={()=>setKind(k)}>{k[0]}–{k[1]}</button>)}</div>
    <div className="plot-controls">{(['zoom','pan','reset','export'] as const).map((action,i)=><button type="button" key={action} disabled={!ready||!!error} onClick={()=>void control(action)}>{['Zoom (بزرگ‌نمایی)','Pan (جابه‌جایی)','Reset (بازنشانی)','PNG (ذخیره)'][i]}</button>)}</div>
    {error?<div role="alert" className="diagram-message"><Icon name="chart"/><span>{error}</span><button type="button" className="diagram-retry" onClick={()=>setAttempt(n=>n+1)}>Retry (تلاش دوباره)</button></div>:!ready&&<p role="status" className="micro">Loading scientific data / chart… (در حال دریافت نمودار)</p>}
    <div ref={host} className="plotly-host" style={{display:error?'none':undefined}} aria-label={`${kind} scientific chart`} aria-busy={!ready}/>
    {actionError&&<p role="alert" className="micro">{actionError}</p>}
    <p className="micro">{kind==='Ts'?'Linear T and s axes':'Logarithmic pressure axis'}{kind==='Pv'?' · Logarithmic specific volume':''}<br/>زیر نقطه بحرانی: سمت مایع در چپ مرز آبی؛ ناحیه دوفازی بین مرزها؛ سمت بخار در راست مرز بنفش.</p>
    {result&&!markerAllowed(result)&&<p role="status" className="plot-warning">State marker withheld: uniqueness is not certified. نقطه حالت به‌علت تأییدنشدن یکتایی نمایش داده نمی‌شود.</p>}
    {!result&&<p className="micro">No unique calculated state selected (حالت یکتای محاسبه‌شده انتخاب نشده)</p>}
    {data&&<details className="plot-domain"><summary>Domain & limitations (محدوده و محدودیت‌ها)</summary><p>Computed range: {data.domain.minimum_T_c.toFixed(3)}–{data.domain.maximum_T_c.toFixed(3)} °C. Critical T={data.critical.T.toFixed(3)} °C, P={data.critical.P.toFixed(0)} kPa.</p><p lang="fa">فاصله نهایی ۰٫۰۵ کلوین تا نقطه بحرانی رسم نمی‌شود. رنگ ناحیه دوفازی در آخرین نمونه متوقف می‌شود و رأس بحرانی نیست. یخ، حالت‌های شبه‌پایدار و مرز کامل اعتبار IF97 در این نمودارها نمایش داده نمی‌شوند. بالای نقطه بحرانی تقسیم‌بندی مایع/بخار کاربرد ندارد.</p>{data.warnings.map(w=><p key={w}>{w}</p>)}</details>}
  </section>;
}
