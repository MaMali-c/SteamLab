/** Live integration tests: require a running real backend. No scientific fixtures. */
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeAll, beforeEach, afterEach, it, expect, vi } from 'vitest';
import App from './App';
import { PAIRS, PARAMETERS } from './model';
import { validateResult } from './api';

// jsdom has no real SVG layout; chart rendering is checked in the browser.
// Only the renderer is stubbed; all thermodynamic requests use the live API.
vi.mock('plotly.js-basic-dist-min',()=>({default:{react:async()=>{},purge:()=>{},Plots:{resize:async()=>{}}}}));

const base=process.env.TERMOYAZD_TEST_API || 'http://127.0.0.1:8000';
const realFetch=globalThis.fetch;
let state: Record<string,number>;
let saturated: Record<string,number>;
async function api(pair:string,values:Record<string,number>) {
  const response=await realFetch(base+'/api/calculate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({input_pair:pair,values})});
  return {response,data:await response.json()};
}
beforeAll(async()=>{
  const single=await api('T_P',{T:300,P:500});
  const mixture=await api('P_x',{P:500,x:.35});
  if (!single.response.ok || !mixture.response.ok) throw new Error('Real backend seed calculations failed; no mock fallback is allowed.');
  state=single.data.full_state; saturated={...mixture.data.full_state,x:.35};
},60000);
beforeEach(()=>{
  // jsdom AbortSignal and Node fetch belong to different realms. The browser
  // cancellation behavior is exercised separately in the real browser.
  vi.stubGlobal('fetch',(url:RequestInfo|URL,init?:RequestInit)=>realFetch(typeof url==='string'&&url.startsWith('/')?base+url:url,{...init,signal:undefined}));
});
afterEach(()=>vi.unstubAllGlobals());

it.each(PAIRS)('real API and user interface: $id',async(pair)=>{
  const source=pair.parameters.includes('x')?saturated:state;
  const values=Object.fromEntries(pair.parameters.map(key=>[key,source[key]]));
  const direct=await api(pair.parameters.join('_'),values);
  render(<App/>);
  const choices=within(screen.getByRole('group',{name:/Select input pair/})).getAllByRole('button');
  expect(choices).toHaveLength(11);
  await userEvent.click(choices[PAIRS.findIndex(p=>p.id===pair.id)]);
  expect(screen.getAllByRole('spinbutton')).toHaveLength(2);
  for(const key of pair.parameters){
    const field=screen.getByRole('spinbutton',{name:new RegExp(PARAMETERS[key].name)});
    await userEvent.clear(field); await userEvent.type(field,String(values[key]));
  }
  await userEvent.click(screen.getByRole('button',{name:/^Calculate/}));
  if(!direct.response.ok){
    expect(direct.response.status).toBe(422);
    expect(direct.data.error.code).toBe('ambiguous_state');
    expect(direct.data.error.candidates.length).toBeGreaterThan(1);
    await waitFor(()=>expect(screen.getByRole('alert')).toHaveTextContent('candidate'),{timeout:60000});
    expect(screen.getByRole('button',{name:/Copy results/})).toBeDisabled();
  }else{
    const validated=validateResult(direct.data,pair.id,values);
    expect(validated.convergence.converged).toBe(true);
    await waitFor(()=>expect(screen.queryByText('Valid thermodynamic state') || screen.queryAllByRole('alert')[0]).toBeTruthy(),{timeout:10000});
    if(screen.queryAllByRole('alert')[0]) throw Error(screen.getAllByRole('alert').map(e=>e.textContent).join('; ') || 'UI error');
    expect(screen.getByText('Valid thermodynamic state')).toBeInTheDocument();
    expect(screen.getAllByRole('article')).toHaveLength(4);
    expect(screen.getByRole('button',{name:/Copy results/})).toBeEnabled();
    await userEvent.clear(screen.getAllByRole('spinbutton')[0]);
    expect(screen.queryByText('Valid thermodynamic state')).not.toBeInTheDocument();
    expect(screen.getByRole('button',{name:/Copy results/})).toBeDisabled();
  }
},120000);

it('real API rejects invalid quality without showing success',async()=>{
  const direct=await api('P_x',{P:500,x:1.2});
  expect(direct.response.status).toBe(422);
  render(<App/>);
  const choices=within(screen.getByRole('group',{name:/Select input pair/})).getAllByRole('button');
  await userEvent.click(choices[2]);
  await userEvent.type(screen.getByRole('spinbutton',{name:/Pressure/}),'500');
  await userEvent.type(screen.getByRole('spinbutton',{name:/Steam quality/}),'1.2');
  await userEvent.click(screen.getByRole('button',{name:/^Calculate/}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Quality');
  expect(screen.queryByText('Valid thermodynamic state')).not.toBeInTheDocument();
});
