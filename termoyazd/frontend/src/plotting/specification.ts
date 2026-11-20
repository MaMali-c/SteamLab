import type { StateResult } from '../api';
import type { SaturationData } from './data';
export type DiagramKind='Ts'|'Pv'|'Ph';
const axes={Ts:{f:'sf',g:'sg',y:'T',stateX:'s',xUnit:'kJ/(kg·K)',yUnit:'°C',xTitle:'Entropy s',yTitle:'Temperature T'},Pv:{f:'vf',g:'vg',y:'P',stateX:'v',xUnit:'m³/kg',yUnit:'kPa',xTitle:'Specific volume v',yTitle:'Pressure P'},Ph:{f:'hf',g:'hg',y:'P',stateX:'h',xUnit:'kJ/kg',yUnit:'kPa',xTitle:'Enthalpy h',yTitle:'Pressure P'}} as const;
export function markerAllowed(state:StateResult|null):boolean {
  return !!state && state.convergence.converged && state.convergence.verified_candidates===1 && state.convergence.uniqueness_certified;
}
export function buildDiagram(kind:DiagramKind,data:SaturationData,state:StateResult|null){
  const a=axes[kind], rows=data.points;
  const xf=rows.map(p=>p[a.f]),xg=rows.map(p=>p[a.g]),y=rows.map(p=>p[a.y]);
  const hover=`${a.xTitle}: %{x:.6g} ${a.xUnit}<br>${a.yTitle}: %{y:.6g} ${a.yUnit}<extra>%{fullData.name}</extra>`;
  // Fill stops at the final computed sample; it does not invent a critical apex.
  const traces:object[]=[{type:'scatter',mode:'lines',x:[...xf,...[...xg].reverse()],y:[...y,...[...y].reverse()],fill:'toself',fillcolor:'rgba(37,99,235,0.13)',line:{width:0},hoverinfo:'skip',name:'Two-phase band (دوفازی)',showlegend:true},
    {type:'scatter',mode:'lines',x:xf,y,name:'Saturated liquid (مایع اشباع)',line:{color:'#00B8FF',width:2,shape:'linear'},hovertemplate:hover},
    {type:'scatter',mode:'lines',x:xg,y,name:'Saturated vapor (بخار اشباع)',line:{color:'#A78BFA',width:2,shape:'linear'},hovertemplate:hover}];
  if(markerAllowed(state)){
    const x=state!.properties[a.stateX], sy=state!.properties[a.y];
    if(Number.isFinite(x)&&Number.isFinite(sy)&&(kind==='Ts'||sy>0)&&(kind!=='Pv'||x>0))traces.push({type:'scatter',mode:'markers',x:[x],y:[sy],name:'Calculated state (حالت محاسبه‌شده)',marker:{color:'#FFB284',size:10,line:{color:'#F8FAFC',width:1}},hovertemplate:hover});
  }
  const axis={gridcolor:'#2B405B',zeroline:false,automargin:true,tickfont:{size:10,color:'#94A3B8'},showline:true,linecolor:'#49627F'};
  return {traces,layout:{paper_bgcolor:'#111E33',plot_bgcolor:'#0B1426',font:{family:'Arial, sans-serif',color:'#F8FAFC',size:11},margin:{l:55,r:15,t:24,b:130},height:480,autosize:true,dragmode:'zoom',hovermode:'closest',uirevision:`${kind}-${state?JSON.stringify(state.properties):'empty'}`,xaxis:{...axis,title:{text:`${a.xTitle} [${a.xUnit}]`},type:kind==='Pv'?'log':'linear'},yaxis:{...axis,title:{text:`${a.yTitle} [${a.yUnit}]`},type:kind==='Ts'?'linear':'log'},legend:{orientation:'h',x:0,y:-.32,font:{size:9}},annotations:[{xref:'paper',yref:'paper',x:1,y:1.06,xanchor:'right',showarrow:false,text:'Critical apex excluded · رأس بحرانی رسم نشده',font:{size:9,color:'#94A3B8'}}]},config:{responsive:true,displaylogo:false,scrollZoom:false,displayModeBar:false,modeBarButtonsToRemove:['select2d','lasso2d'],toImageButtonOptions:{format:'png',filename:`termoyazd-${kind}`,width:1400,height:1000,scale:2}}};
}
