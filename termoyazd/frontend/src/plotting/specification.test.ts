import { it, expect } from 'vitest';
import { buildDiagram, markerAllowed } from './specification';
import { validateResult } from '../api';
// Real API only: no invented curves or scientific state fixtures.
it('projects real saturation samples into all three diagrams',async()=>{
  const base=process.env.TERMOYAZD_TEST_API||'http://127.0.0.1:8000';
  const raw=await fetch(base+'/api/diagrams/saturation');
  expect(raw.ok).toBe(true);
  const data=await raw.json();
  for(const kind of ['Ts','Pv','Ph'] as const){
    const spec=buildDiagram(kind,data,null);
    expect(spec.traces).toHaveLength(3);
    expect(spec.layout.yaxis.type).toBe(kind==='Ts'?'linear':'log');
    expect(spec.layout.xaxis.type).toBe(kind==='Pv'?'log':'linear');
  }
  const response=await fetch(base+'/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({input_pair:'T_P',values:{T:300,P:1000}})});
  expect(response.ok).toBe(true);
  const state=validateResult(await response.json(),'TP',{T:300,P:1000});
  expect(markerAllowed(state)).toBe(true);
  expect(buildDiagram('Ts',data,state).traces).toHaveLength(4);
  expect(markerAllowed({...state,convergence:{...state.convergence,uniqueness_certified:false}})).toBe(false);
  expect(markerAllowed(null)).toBe(false);
},60000);
