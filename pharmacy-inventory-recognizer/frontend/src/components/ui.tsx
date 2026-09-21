import type { ReactNode } from "react";

const CAT_COLORS = ["--c0","--c1","--c4","--c2","--c4","--c5","--c6","--c7"];
export const catColor = (i:number) => `var(${CAT_COLORS[i % CAT_COLORS.length]})`;

export function StatCard({ value, label, icon, tint }:{
  value:ReactNode; label:string; icon:ReactNode; tint:string;
}){
  return (
    <div className="stat">
      <div className="ic" style={{background:tint+"22",color:tint}}>{icon}</div>
      <div className="val">{value}</div>
      <div className="lbl">{label}</div>
    </div>
  );
}

export function StatusBadge({ status }:{ status:string }){
  const cls = status==="In Stock" ? "b-ok" : status==="Low Stock" ? "b-warn"
    : status==="Out of Stock" ? "b-bad"
    : status==="Fulfilled" ? "b-ok" : status==="Processing" ? "b-info"
    : status==="Pending" ? "b-warn" : status==="Cancelled" ? "b-bad" : "b-mut";
  return <span className={`badge ${cls}`}>{status}</span>;
}
