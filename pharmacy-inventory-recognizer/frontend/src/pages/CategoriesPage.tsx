import { useEffect, useState } from "react";
import { getCategories, addCategory, delCategory } from "../api";
import type { Category } from "../types";
import { StatusBadge, catColor } from "../components/ui";
import { peso } from "../lib/dfa";
import { loadAuth } from "../lib/auth";

export default function CategoriesPage(){
  const [cats,setCats]=useState<Category[]>([]); const [q,setQ]=useState(""); const [err,setErr]=useState("");
  const [openId,setOpenId]=useState<number|null>(null); const [name,setName]=useState("");
  const canEdit=["admin","inventory_manager"].includes(loadAuth()?.role||"");
  const load=()=>getCategories().then(setCats).catch(e=>setErr(e.message));
  useEffect(()=>{ load(); },[]);
  const shown=cats.filter(c=>c.name.toLowerCase().includes(q.trim().toLowerCase()));
  const totalMeds=cats.reduce((a,c)=>a+c.sku_count,0);
  async function add(){ if(!name.trim())return; try{ await addCategory(name.trim(),""); setName(""); setErr(""); load(); }catch(e){ setErr((e as Error).message); } }
  async function remove(c:Category){ if(!confirm(`Delete ${c.name}?`))return; try{ await delCategory(c.category_id); load(); }catch(e){ setErr((e as Error).message); } }

  return (
    <>
      <h2 className="page-h">Categories</h2>
      <p className="page-sub">{cats.length} categories · {totalMeds} total medicines</p>
      {err && <div className="err">{err}</div>}
      <div className="toolbar">
        <div className="search"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
          <input placeholder="Search categories…" value={q} onChange={e=>setQ(e.target.value)}/></div>
        {canEdit && <>
          <input placeholder="New category" value={name} style={{width:170}} onChange={e=>setName(e.target.value)} onKeyDown={e=>e.key==="Enter"&&add()}/>
          <button className="btn" onClick={add}>＋ Add Category</button></>}
      </div>
      {shown.map((c,i)=>(
        <div className="exp" key={c.category_id}>
          <div className="exp-head" onClick={()=>setOpenId(openId===c.category_id?null:c.category_id)}>
            <span className="dot-c" style={{background:catColor(i)}}/>
            <div style={{flex:1}}><b>{c.name}</b> <span style={{color:"var(--muted)",fontSize:12}}>{c.description}</span></div>
            <div className="metric"><b>{c.sku_count}</b><span>SKUs</span></div>
            <div className="metric"><b>{c.units}</b><span>Units</span></div>
            <div className="metric"><b>{peso(c.value)}</b><span>Value</span></div>
            {c.alerts>0 && <span className="badge b-warn">⚠ {c.alerts} alert</span>}
            {canEdit && <button className="iconbtn" title="Delete" onClick={e=>{e.stopPropagation();remove(c);}}>🗑</button>}
            <span className={`chev ${openId===c.category_id?"open":""}`}>›</span>
          </div>
          {openId===c.category_id && (
            <div className="exp-body">
              {c.products.length ? <table>
                <thead><tr><th>Code</th><th>Name</th><th>Price</th><th>Stock</th><th>Status</th></tr></thead>
                <tbody>{c.products.map(p=>(
                  <tr key={p.product_id}><td><span className="code">{p.sku}</span></td><td>{p.name}</td>
                    <td>{peso(p.price)}</td><td>{p.stock}</td><td><StatusBadge status={p.status}/></td></tr>
                ))}</tbody></table> : <p style={{color:"var(--muted)",fontSize:13,padding:"8px 0"}}>No medicines in this category.</p>}
            </div>
          )}
        </div>
      ))}
    </>
  );
}
