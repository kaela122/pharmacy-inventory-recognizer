import { useEffect, useState } from "react";
import { getAnalytics } from "../api";
import type { Analytics } from "../types";
import { StatusBadge } from "../components/ui";
import { BarChart, Donut } from "../components/charts";

export default function AnalyticsPage(){
  const [a,setA]=useState<Analytics|null>(null); const [err,setErr]=useState("");
  useEffect(()=>{ getAnalytics().then(setA).catch(e=>setErr(e.message)); },[]);
  if(err) return <div className="err">{err}</div>;
  if(!a) return <p style={{color:"var(--muted)"}}>Loading…</p>;
  const statusColors=["var(--ok)","var(--warn)","var(--bad)"];
  return (
    <>
      <h2 className="page-h">Analytics</h2><p className="page-sub">Inventory insights</p>
      <div className="grid2">
        <div className="panel"><h2>Stock units by category</h2><BarChart data={a.stock_by_category}/></div>
        <div className="panel"><h2>Status distribution</h2><Donut data={a.status_distribution} colors={statusColors}/></div>
      </div>
      <div className="panel"><h2>Inventory value by category (₱)</h2><BarChart data={a.value_by_category} money/></div>
      <div className="panel">
        <h2>⚠️ Needs restocking</h2>
        <table><thead><tr><th>Code</th><th>Medicine</th><th>Stock</th><th>Reorder at</th><th>Status</th></tr></thead>
          <tbody>{a.restocking.map(r=>(
            <tr key={r.sku}><td><span className="code">{r.sku}</span></td><td>{r.name}</td>
              <td style={{color:r.status==="Out of Stock"?"var(--bad)":"var(--warn)"}}>{r.stock}</td>
              <td style={{color:"var(--muted)"}}>{r.reorder_level}</td><td><StatusBadge status={r.status}/></td></tr>
          ))}</tbody></table>
      </div>
    </>
  );
}
