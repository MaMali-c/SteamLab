import { browserFetch } from './browserEngine';
import { apiAddress } from './config';
import { PAIRS, OUTPUT_UNITS, outputParameters, type PairId } from './model';
export type Properties = { T:number; P:number; h:number; u:number; s:number; v:number };
export type StateResult = {
  fluid: string; input_pair: PairId; properties: Properties; units: Record<keyof Properties,string>;
  phase:string; region:number; quality:number|null; quality_note:string; method:string; warnings:string[];
  saturation: Record<string,number>; normalized_inputs: Record<string,number>;
  convergence: { converged:boolean; residuals:Record<string,number>; tolerances:Record<string,number>; evaluations:number; verified_candidates:number; uniqueness_certified:boolean };
};
export function validateResult(raw: unknown, pair: PairId, inputs: Record<string,number>): StateResult {
  const fail = (): never => { throw new Error('Invalid or inconsistent API response. پاسخ موتور علمی معتبر یا سازگار با ورودی نیست.'); };
  if (!raw || typeof raw !== 'object') return fail();
  const r = raw as Record<string, any>;
  const keys = Object.keys(OUTPUT_UNITS) as (keyof Properties)[];
  const finite = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
  if (r.input_pair !== PAIRS.find(p=>p.id===pair)!.parameters.join('_') || !r.full_state || !keys.every(k=>finite(r.full_state[k])) || ![1,2,3,4,5].includes(r.region) || typeof r.phase!=='string' || !r.phase || typeof r.solver_method!=='string') return fail();
  if (r.quality !== null && (!finite(r.quality) || r.quality<0 || r.quality>1)) return fail();
  if (!r.convergence || r.convergence.converged!==true || typeof r.convergence.uniqueness_certified!=='boolean' || !Number.isInteger(r.convergence.evaluations) || r.convergence.evaluations<0 || r.convergence.verified_candidates!==1) return fail();
  if (!r.normalized_inputs || Object.keys(r.normalized_inputs).length!==Object.keys(inputs).length) return fail();
  for (const [key,value] of Object.entries(inputs)) {
    const tol=r.convergence.tolerances?.[key], residual=r.convergence.residuals?.[key];
    const actual=key==='x'?r.quality:r.full_state[key];
    if (!finite(r.normalized_inputs[key]) || Math.abs(r.normalized_inputs[key]-value)>1e-10*Math.max(1,Math.abs(value)) || !finite(tol) || tol<0 || !finite(residual) || Math.abs(residual)>tol || !finite(actual) || Math.abs(actual-value)>tol) return fail();
  }
  const outputs=outputParameters(pair);
  if (!r.calculated_properties || Object.keys(r.calculated_properties).length!==4 || !outputs.every(k=>finite(r.calculated_properties[k]) && r.calculated_properties[k]===r.full_state[k])) return fail();
  if (!r.saturation || typeof r.saturation!=='object' || !Object.entries(r.saturation).every(([k,v])=>['temperature_at_P_c','pressure_at_T_kpa'].includes(k)&&finite(v))) return fail();
  if (!Array.isArray(r.scientific_warnings) || !r.scientific_warnings.every((v:unknown)=>typeof v==='string')) return fail();
  return {fluid:'Water',input_pair:pair,properties:r.full_state,units:OUTPUT_UNITS,phase:r.phase,region:r.region,quality:r.quality,quality_note:'Quality is defined only at liquid–vapor coexistence.',method:r.solver_method,warnings:r.scientific_warnings,saturation:r.saturation,normalized_inputs:r.normalized_inputs,convergence:r.convergence};
}
export type SatPoint = { T: number; sf: number; sg: number };

export async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  init?.signal?.addEventListener('abort', abort, { once: true });
  if (init?.signal?.aborted) controller.abort();
  let timedOut = false;
  const timer = window.setTimeout(() => { timedOut = true; controller.abort(); }, 180000);
  try {
  const response = await (import.meta.env.VITE_BROWSER_ENGINE === 'true' ? browserFetch(url, { ...init, signal: controller.signal }) : fetch(apiAddress(url), { ...init, signal: controller.signal }));
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof data?.detail === 'string' ? data.detail : 'Check the input fields and units.';
    const explanations: Record<string,string> = { ambiguous_state:'چند حالت معتبر یافت شد؛ یک خاصیت مستقل دیگر برای تعیین حالت لازم است.', ambiguous_saturation:'دما و فشار اشباع برای تعیین کیفیت کافی نیستند.', search_incomplete:'جست‌وجوی عددی کامل نشده؛ نتیجه‌ای انتخاب نشد.', no_verified_state:'حالت معتبر با این ورودی‌ها پیدا نشد.', quality_domain:'کیفیت بخار خارج از محدوده اشباع معتبر است.', invalid_quality:'کیفیت باید بین صفر و یک باشد.', server_busy:'موتور علمی مشغول است؛ چند لحظه دیگر دوباره تلاش کنید.', request_too_large:'حجم درخواست بیشتر از حد مجاز است.' };
    const code=data?.error?.code;
    throw new Error([data?.error?.message || `${detail} (HTTP ${response.status})`, explanations[code], Array.isArray(data?.error?.candidates)&&data.error.candidates.length ? `${data.error.candidates.length} candidate states (حالت‌های ممکن)` : ''].filter(Boolean).join(' — '));
  }
  if (!data) throw new Error('The API returned an unreadable response. Check that both services are running.');
  return data as T;
  } catch (error) {
    if (timedOut) throw new Error('The API request timed out. Try again. زمان پاسخ‌گویی موتور علمی تمام شد؛ دوباره تلاش کنید.');
    throw error;
  } finally {
    window.clearTimeout(timer);
    init?.signal?.removeEventListener('abort', abort);
  }
}

export function toEngineeringUnits(t: number, tu: string, p: number, pu: string) {
  const pressureFactors: Record<string, number> = { kPa: 1, MPa: 1000, bar: 100 };
  return { temperature_c: tu === 'K' ? t - 273.15 : t,
    pressure_kpa: p * (pressureFactors[pu] ?? 1) };
}
