import { request } from '../api';
export type Sample={T:number;P:number;sf:number;sg:number;vf:number;vg:number;hf:number;hg:number};
export type SaturationData={method:string;points:Sample[];units:Record<string,string>;critical:{T:number;P:number;included:false};domain:{minimum_T_c:number;maximum_T_c:number;critical_gap_K:number};warnings:string[]};
let cached:Promise<SaturationData>|null=null;
export function loadSaturation():Promise<SaturationData>{
  if(!cached) cached=request<unknown>('/api/diagrams/saturation').then(value=>{
    const data=value as SaturationData;
    if(!data || data.method!=='IAPWS-IF97' || !Array.isArray(data.points) || data.points.length<2 || !data.critical || data.critical.included!==false || !Number.isFinite(data.critical.T) || !Number.isFinite(data.critical.P) || !data.domain || !(data.domain.critical_gap_K>0) || !Array.isArray(data.warnings) || !data.warnings.every(w=>typeof w==='string')) throw Error('Invalid saturation dataset');
    const units={T:'°C',P:'kPa',s:'kJ/(kg·K)',v:'m³/kg',h:'kJ/kg'};
    if(!Object.entries(units).every(([key,unit])=>data.units?.[key]===unit)) throw Error('Inconsistent diagram units');
    data.points.forEach((p,i)=>{if(!['T','P','sf','sg','vf','vg','hf','hg'].every(k=>Number.isFinite(p[k as keyof Sample])) || p.P<=0 || p.vf<=0 || p.vg<=p.vf || p.sg<=p.sf || p.hg<=p.hf || p.T>=data.critical.T || p.P>=data.critical.P || (i>0 && (p.T<=data.points[i-1].T || p.P<=data.points[i-1].P))) throw Error('Invalid or unordered saturation sample');});
    return data;
  }).catch(error=>{cached=null;throw error;});
  return cached;
}
