import { useEffect, useState } from "react";
import { getStats } from "../api";
import type { Stats } from "../types";
import { StatCard, StatusBadge } from "../components/ui";
import { HBars } from "../components/charts";

export default function DashboardPage(){
  const [s,setS]=useState<Stats|null>(null); const [err,setErr]=useState("");
  useEffect(()=>{ getStats().then(setS).catch(e=>setErr(e.message)); },[]);
  if(err) return <div className="err">Couldn't load dashboard: {err}</div>;
  if(!s) return <p style={{color:"var(--muted)"}}>Loading…</p>;
  return (
    <>
      <h2 className="page-h">Dashboard</h2><p className="page-sub">Pharmacy inventory overview</p>
      <div className="cards">
        <StatCard value={s.total_units.toLocaleString()} label="Total Units" icon="📦" tint="#10b981"/>
        <StatCard value={s.medicine_skus} label="Medicine SKUs" icon="💊" tint="#3b82f6"/>
        <StatCard value={s.low_stock} label="Low Stock Alerts" icon="⚠️" tint="#fbbf24"/>
        <StatCard value={s.out_of_stock} label="Out of Stock" icon="⛔" tint="#f87171"/>
      </div>
      <div className="panel">
        <h2>⚠️ Low stock alerts <span>{s.alerts.length} items</span></h2>
        {s.alerts.length ? s.alerts.map(a=>(
          <div key={a.sku} style={{display:"flex",alignItems:"center",gap:12,padding:"11px 0",borderTop:"1px solid var(--line)"}}>
            <span className="mono" style={{color:"var(--muted)",fontSize:12,width:44}}>{a.sku}</span>
            <b style={{flex:1}}>{a.name}</b>
            <span style={{color:"var(--muted)",fontSize:13}}>{a.stock} units</span>
            <StatusBadge status={a.status}/>
          </div>
        )) : <p style={{color:"var(--muted)"}}>All items above reorder level.</p>}
      </div>
      <div className="panel"><h2>Category distribution</h2><HBars data={s.category_distribution}/></div>
    </>
  );
}
