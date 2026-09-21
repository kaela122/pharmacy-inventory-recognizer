import { useEffect, useState } from "react";
import { getOrders, getOrderStats, setOrderStatus } from "../api";
import type { Order, OrderStats } from "../types";
import { StatCard, StatusBadge } from "../components/ui";
import { peso } from "../lib/dfa";
import { loadAuth } from "../lib/auth";

const TABS = ["All","Pending","Processing","Fulfilled","Cancelled"];
const CAN_MANAGE = ["admin","inventory_manager"];

export default function OrdersPage(){
  const [orders,setOrders]=useState<Order[]>([]); const [stats,setStats]=useState<OrderStats|null>(null);
  const [q,setQ]=useState(""); const [tab,setTab]=useState("All"); const [openId,setOpenId]=useState<number|null>(null);
  const [err,setErr]=useState(""); const [busyId,setBusyId]=useState<number|null>(null);
  const canManage = CAN_MANAGE.includes(loadAuth()?.role ?? "");
  useEffect(()=>{ refresh(); },[]);
  function refresh(){
    getOrders().then(setOrders).catch(e=>setErr(e.message));
    getOrderStats().then(setStats).catch(()=>{});
  }
  async function moveTo(id:number, status:string){
    setBusyId(id); setErr("");
    try{
      const updated = await setOrderStatus(id, status);
      setOrders(prev=>prev.map(o=>o.order_id===id?updated:o));
      getOrderStats().then(setStats).catch(()=>{});
    }catch(e:any){ setErr(e.message); }
    finally{ setBusyId(null); }
  }
  if(err) return <div className="err">{err}</div>;
  const shown=orders.filter(o=>(tab==="All"||o.status===tab) &&
    (`${o.order_number} ${o.supplier_name}`.toLowerCase().includes(q.trim().toLowerCase())));

  return (
    <>
      <h2 className="page-h">Orders</h2><p className="page-sub">Purchase orders from suppliers</p>
      {stats && <div className="cards">
        <StatCard value={stats.total_orders} label="Total Orders" icon="🛒" tint="#10b981"/>
        <StatCard value={stats.pending} label="Pending" icon="🕐" tint="#fbbf24"/>
        <StatCard value={stats.fulfilled} label="Fulfilled" icon="✅" tint="#34d399"/>
        <StatCard value={peso(stats.total_value)} label="Total Value" icon="💰" tint="#3b82f6"/>
      </div>}
      <div className="toolbar">
        <div className="search"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
          <input placeholder="Search orders or suppliers…" value={q} onChange={e=>setQ(e.target.value)}/></div>
        <div className="tabs">{TABS.map(t=>(<button key={t} className={`tab ${tab===t?"active":""}`} onClick={()=>setTab(t)}>{t}</button>))}</div>
      </div>
      {shown.map(o=>(
        <div className="exp" key={o.order_id}>
          <div className="exp-head" onClick={()=>setOpenId(openId===o.order_id?null:o.order_id)}>
            <div style={{flex:1}}>
              <div style={{display:"flex",alignItems:"center",gap:10}}><b className="mono">{o.order_number}</b><StatusBadge status={o.status}/></div>
              <div style={{color:"var(--muted)",fontSize:12,marginTop:3}}>📅 {o.order_date} · {o.supplier_name} · {o.item_count} items</div>
            </div>
            <b>{peso(o.total)}</b>
            <span className={`chev ${openId===o.order_id?"open":""}`}>›</span>
          </div>
          {openId===o.order_id && (
            <div className="exp-body">
              <table>
                <thead><tr><th>Code</th><th>Medicine</th><th style={{textAlign:"right"}}>Qty</th><th style={{textAlign:"right"}}>Subtotal</th></tr></thead>
                <tbody>{o.items.map((it,i)=>(
                  <tr key={i}><td><span className="code">{it.sku}</span></td><td>{it.name}</td>
                    <td style={{textAlign:"right"}}>{it.quantity}</td><td style={{textAlign:"right"}}>{peso(it.subtotal)}</td></tr>
                ))}</tbody>
              </table>
              {canManage && (o.status==="Pending"||o.status==="Processing") && (
                <div style={{display:"flex",gap:10,marginTop:12}} onClick={e=>e.stopPropagation()}>
                  {o.status==="Pending" && (
                    <button className="btn info" disabled={busyId===o.order_id} onClick={()=>moveTo(o.order_id,"Processing")}>
                      {busyId===o.order_id?"Working…":"Mark Processing"}</button>
                  )}
                  {o.status==="Processing" && (
                    <button className="btn ok" disabled={busyId===o.order_id} onClick={()=>moveTo(o.order_id,"Fulfilled")}>
                      {busyId===o.order_id?"Working…":"Mark Fulfilled"}</button>
                  )}
                  <button className="btn danger" disabled={busyId===o.order_id} onClick={()=>moveTo(o.order_id,"Cancelled")}>
                    Cancel Order</button>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </>
  );
}
