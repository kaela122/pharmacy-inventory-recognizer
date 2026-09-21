import { useState } from "react";
import type { Slice } from "../types";
import { catColor } from "./ui";

// Vertical bars, one color per category, with y-axis labels and a hover tooltip.
export function BarChart({ data, money=false }:{ data:Slice[]; money?:boolean }){
  const w=760, h=230, padL=48, padB=34, padT=12;
  const [hover,setHover]=useState<number|null>(null);
  const max = Math.max(1, ...data.map(d=>d.value));
  const nice = niceMax(max);
  const bw = (w-padL-10)/Math.max(1,data.length);
  const y = (v:number)=> padT + (1 - v/nice)*(h-padT-padB);
  const ticks = [0,0.25,0.5,0.75,1].map(f=>f*nice);
  const fmt = (v:number)=> money ? "₱"+abbr(v) : String(Math.round(v));
  const bars = data.map((d,i)=>{
    const bh=(d.value/nice)*(h-padT-padB), x=padL+i*bw+bw*0.22, ww=bw*0.56;
    return { d, x, ww, top:h-padB-bh, bh:Math.max(0,bh) };
  });
  const hovered = hover!==null ? bars[hover] : null;
  return (
    <div className="chart-wrap">
      <svg className="chart" viewBox={`0 0 ${w} ${h}`} onMouseLeave={()=>setHover(null)}>
        {ticks.map((t,i)=>(
          <g key={i}>
            <line x1={padL} x2={w-6} y1={y(t)} y2={y(t)} stroke="var(--line)" strokeDasharray="3 4"/>
            <text x={padL-8} y={y(t)+4} textAnchor="end" fill="var(--faint)" fontSize="10">{fmt(t)}</text>
          </g>
        ))}
        {bars.map((b,i)=>(
          <g key={i}>
            <rect x={b.x} y={b.top} width={b.ww} height={b.bh} rx={4}
              fill={catColor(i)} opacity={hover===null||hover===i?1:0.45}
              onMouseEnter={()=>setHover(i)} onMouseMove={()=>setHover(i)}
              style={{cursor:"pointer",transition:"opacity .12s"}}/>
            <rect x={b.x} y={padT} width={b.ww} height={h-padT-padB} fill="transparent"
              onMouseEnter={()=>setHover(i)} onMouseMove={()=>setHover(i)} style={{cursor:"pointer"}}/>
            <text x={b.x+b.ww/2} y={h-padB+15} textAnchor="middle" fill="var(--muted)" fontSize="10">
              {b.d.label.length>10?b.d.label.slice(0,9)+"…":b.d.label}</text>
          </g>
        ))}
      </svg>
      {hovered && (
        <div className="chart-tip" style={{
          left:`${((hovered.x+hovered.ww/2)/w)*100}%`,
          top:`${(hovered.top/h)*100}%`,
        }}>
          <b>{hovered.d.label}</b>
          <span>{money?"value":"stock"} <em>{fmt(hovered.d.value)}</em></span>
        </div>
      )}
    </div>
  );
}

// Donut with legend + counts (for status distribution).
export function Donut({ data, colors }:{ data:Slice[]; colors:string[] }){
  const size=180, r=62, cx=size/2, cy=size/2, C=2*Math.PI*r;
  const total=data.reduce((a,s)=>a+s.value,0)||1; let off=0;
  return (
    <div style={{display:"flex",gap:22,alignItems:"center",flexWrap:"wrap"}}>
      <svg viewBox={`0 0 ${size} ${size}`} style={{width:160,flexShrink:0}}>
        {data.map((s,i)=>{ const len=s.value/total*C; const el=(
          <circle key={i} cx={cx} cy={cy} r={r} fill="none" stroke={colors[i]} strokeWidth={20}
            strokeDasharray={`${len} ${C-len}`} strokeDashoffset={-off} transform={`rotate(-90 ${cx} ${cy})`}/>
        ); off+=len; return el; })}
      </svg>
      <div className="legend" style={{flex:1,minWidth:130}}>
        {data.map((s,i)=>(
          <div className="legend-row" key={i}>
            <span className="sw" style={{background:colors[i]}}/><span>{s.label}</span>
            <span className="lv">{s.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Horizontal bars (dashboard category distribution).
export function HBars({ data }:{ data:Slice[] }){
  const max=Math.max(1,...data.map(d=>d.value));
  return (
    <div>
      {data.map((d,i)=>(
        <div key={i} style={{display:"flex",alignItems:"center",gap:12,marginBottom:10,fontSize:12.5}}>
          <span style={{width:110,color:"var(--muted)"}}>{d.label}</span>
          <div style={{flex:1,height:8,background:"#0d1318",borderRadius:999,overflow:"hidden"}}>
            <span style={{display:"block",height:"100%",width:`${d.value/max*100}%`,background:"var(--accent)",borderRadius:999}}/>
          </div>
          <b style={{width:24,textAlign:"right"}}>{d.value}</b>
        </div>
      ))}
    </div>
  );
}

function niceMax(v:number){ const p=Math.pow(10,Math.floor(Math.log10(v))); const n=v/p;
  const m = n<=1?1:n<=2?2:n<=3?3:n<=5?5:10; return m*p; }
function abbr(v:number){ return v>=1000 ? (v/1000).toFixed(v%1000?1:0)+"k" : String(Math.round(v)); }
