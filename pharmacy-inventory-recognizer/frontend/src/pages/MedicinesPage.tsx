import { useEffect, useState } from "react";
import { getProducts, getCategories, addProduct, editProduct, delProduct,
         recordMovement, getHistory } from "../api";
import type { Product, Category, ProductInput, Movement, MovementInput } from "../types";
import { StatusBadge } from "../components/ui";
import { runDFA, dfaReason, peso } from "../lib/dfa";
import { loadAuth } from "../lib/auth";

const EMPTY:ProductInput = { sku:"", name:"", category_id:null, price:0, reorder_level:20, stock:0 };
const TABS = ["All","In Stock","Low Stock","Out of Stock"];

export default function MedicinesPage(){
  const [items,setItems]=useState<Product[]>([]);
  const [cats,setCats]=useState<Category[]>([]);
  const [err,setErr]=useState(""); const [q,setQ]=useState(""); const [tab,setTab]=useState("All");
  const [open,setOpen]=useState(false); const [editId,setEditId]=useState<number|null>(null);
  const [form,setForm]=useState<ProductInput>(EMPTY);
  // stock movement + history modals
  const [stockFor,setStockFor]=useState<Product|null>(null);
  const [move,setMove]=useState<MovementInput>({movement_type:"in",quantity:0,note:""});
  const [histFor,setHistFor]=useState<Product|null>(null); const [hist,setHist]=useState<Movement[]>([]);
  const role=loadAuth()?.role; const canEdit=role==="admin"||role==="inventory_manager"; const canDelete=role==="admin";

  const load=()=>getProducts().then(setItems).catch(e=>setErr(e.message));
  useEffect(()=>{ load(); getCategories().then(setCats).catch(()=>{}); },[]);

  const code=form.sku.trim().toUpperCase(); const dfa=runDFA(code); const ok=dfa.accepted;
  const totalUnits=items.reduce((a,p)=>a+p.stock,0);
  const shown=items.filter(p=>(tab==="All"||p.status===tab) &&
    (`${p.sku} ${p.name} ${p.category_name??""}`.toLowerCase().includes(q.trim().toLowerCase())));

  function openAdd(){ setEditId(null); setForm({...EMPTY,category_id:cats[0]?.category_id??null}); setErr(""); setOpen(true); }
  function openEdit(p:Product){ setEditId(p.product_id);
    setForm({sku:p.sku,name:p.name,category_id:p.category_id,price:p.price,reorder_level:p.reorder_level,stock:p.stock});
    setErr(""); setOpen(true); }
  async function save(){ if(!ok)return;
    try{ const pl={...form,sku:code}; editId===null?await addProduct(pl):await editProduct(editId,pl); setOpen(false); load(); }
    catch(e){ setErr((e as Error).message); } }
  async function remove(p:Product){ if(!confirm(`Delete ${p.sku}?`))return;
    try{ await delProduct(p.product_id); load(); }catch(e){ setErr((e as Error).message); } }

  function openStock(p:Product){ setStockFor(p); setMove({movement_type:"in",quantity:0,note:""}); setErr(""); }
  async function saveMove(){ if(!stockFor||move.quantity<0)return;
    try{ await recordMovement(stockFor.product_id,move); setStockFor(null); load(); }
    catch(e){ setErr((e as Error).message); } }
  async function openHist(p:Product){ setHistFor(p); setHist([]); try{ setHist(await getHistory(p.product_id)); }catch{} }

  return (
    <>
      <h2 className="page-h">Medicines</h2>
      <div className="rowflex">
        <div><span className="badge b-bad" style={{marginRight:8}}>{totalUnits.toLocaleString()}</span>
          <span style={{color:"var(--muted)",fontSize:13}}>{items.length} medicines</span></div>
        {canEdit && <button className="btn" onClick={openAdd}>＋ Add Medicine</button>}
      </div>
      {err && <div className="err">{err}</div>}
      <div className="toolbar">
        <div className="search"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
          <input placeholder="Search by name or code…" value={q} onChange={e=>setQ(e.target.value)}/></div>
        <div className="tabs">{TABS.map(t=>(
          <button key={t} className={`tab ${tab===t?"active":""}`} onClick={()=>setTab(t)}>{t}</button>))}</div>
      </div>
      <div className="panel" style={{padding:0}}><table>
        <thead><tr><th>Code</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>Status</th><th></th></tr></thead>
        <tbody>{shown.map(p=>(
          <tr key={p.product_id}>
            <td><span className="code">{p.sku}</span></td>
            <td><b>{p.name}</b></td>
            <td style={{color:"var(--muted)"}}>{p.category_name??"—"}</td>
            <td>{peso(p.price)}</td>
            <td><span style={{color:p.status==="In Stock"?"var(--ink)":p.status==="Out of Stock"?"var(--bad)":"var(--warn)"}}>{p.stock}</span>
              <span style={{color:"var(--faint)"}}> / {p.reorder_level}</span></td>
            <td><StatusBadge status={p.status}/></td>
            <td style={{textAlign:"right",whiteSpace:"nowrap"}}>
              <button className="btn ghost sm" onClick={()=>openStock(p)}>Stock</button>{" "}
              <button className="btn ghost sm" onClick={()=>openHist(p)}>History</button>{" "}
              {canEdit && <button className="btn ghost sm" onClick={()=>openEdit(p)}>Edit</button>}{" "}
              {canDelete && <button className="iconbtn" title="Delete" onClick={()=>remove(p)}>🗑</button>}</td>
          </tr>
        ))}{shown.length===0 && <tr><td colSpan={7} style={{color:"var(--muted)",textAlign:"center",padding:24}}>No medicines match.</td></tr>}</tbody>
      </table></div>

      {/* add / edit medicine */}
      {open && (
        <div className="overlay" onClick={e=>e.target===e.currentTarget&&setOpen(false)}>
          <div className="modal">
            <h3>{editId===null?"Add Medicine":"Edit Medicine"}</h3>
            <p className="hint">The product code is validated by the DFA recognizer before saving.</p>
            <div className="field"><label>Product code (M, S or C + 3 digits, e.g. M001)</label>
              <input className="mono" maxLength={8} placeholder="M001" value={form.sku} onChange={e=>setForm({...form,sku:e.target.value})}/>
              {form.sku && <div className={`valid ${ok?"ok":"bad"}`}>{ok?"✓ ACCEPTED — ":"✗ REJECTED — "}{dfaReason(code,dfa)}</div>}</div>
            <div className="field"><label>Medicine name</label>
              <input value={form.name} placeholder="Paracetamol 500mg" onChange={e=>setForm({...form,name:e.target.value})}/></div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
              <div className="field"><label>Category</label>
                <select value={form.category_id??""} onChange={e=>setForm({...form,category_id:Number(e.target.value)})}>
                  {cats.map(c=><option key={c.category_id} value={c.category_id}>{c.name}</option>)}</select></div>
              <div className="field"><label>Price (₱)</label>
                <input type="number" min={0} step="0.01" value={form.price} onChange={e=>setForm({...form,price:Number(e.target.value)})}/></div>
              <div className="field"><label>Stock</label>
                <input type="number" min={0} value={form.stock} onChange={e=>setForm({...form,stock:Number(e.target.value)})}/></div>
              <div className="field"><label>Reorder level</label>
                <input type="number" min={0} value={form.reorder_level} onChange={e=>setForm({...form,reorder_level:Number(e.target.value)})}/></div>
            </div>
            <div className="modal-actions">
              <button className="btn ghost" onClick={()=>setOpen(false)}>Cancel</button>
              <button className="btn" onClick={save} disabled={!ok}>Save</button>
            </div>
          </div>
        </div>
      )}

      {/* record stock movement */}
      {stockFor && (
        <div className="overlay" onClick={e=>e.target===e.currentTarget&&setStockFor(null)}>
          <div className="modal">
            <h3>Stock movement</h3>
            <p className="hint"><span className="code">{stockFor.sku}</span> {stockFor.name} · currently {stockFor.stock} in stock</p>
            <div className="field"><label>Type</label>
              <select value={move.movement_type} onChange={e=>setMove({...move,movement_type:e.target.value})}>
                <option value="in">Stock in (add)</option>
                <option value="out">Stock out (remove / dispense)</option>
                <option value="adjust">Adjust — set exact count</option>
              </select></div>
            <div className="field"><label>{move.movement_type==="adjust"?"New stock count":"Quantity"}</label>
              <input type="number" min={0} value={move.quantity} onChange={e=>setMove({...move,quantity:Number(e.target.value)})}/></div>
            <div className="field"><label>Note (optional)</label>
              <input value={move.note} placeholder="e.g. Delivery from MedCore" onChange={e=>setMove({...move,note:e.target.value})}/></div>
            <div className="modal-actions">
              <button className="btn ghost" onClick={()=>setStockFor(null)}>Cancel</button>
              <button className="btn" onClick={saveMove} disabled={move.quantity<0}>Record</button>
            </div>
          </div>
        </div>
      )}

      {/* movement history */}
      {histFor && (
        <div className="overlay" onClick={e=>e.target===e.currentTarget&&setHistFor(null)}>
          <div className="modal" style={{width:"min(560px,100%)"}}>
            <h3>Stock history</h3>
            <p className="hint"><span className="code">{histFor.sku}</span> {histFor.name}</p>
            {hist.length ? <table>
              <thead><tr><th>When</th><th>Type</th><th style={{textAlign:"right"}}>Change</th><th style={{textAlign:"right"}}>After</th><th>By</th></tr></thead>
              <tbody>{hist.map(m=>(
                <tr key={m.movement_id}>
                  <td style={{color:"var(--muted)",fontSize:12}}>{new Date(m.created_at).toLocaleString([], {month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"})}</td>
                  <td><span className={`badge ${m.movement_type==="in"?"b-ok":m.movement_type==="out"?"b-bad":"b-mut"}`}>{m.movement_type}</span></td>
                  <td style={{textAlign:"right",color:m.change>=0?"var(--ok)":"var(--bad)"}}>{m.change>0?"+":""}{m.change}</td>
                  <td style={{textAlign:"right"}}>{m.resulting_stock}</td>
                  <td className="mono" style={{fontSize:11,color:"var(--muted)"}}>{m.employee_id}</td>
                </tr>
              ))}</tbody></table> : <p style={{color:"var(--muted)",fontSize:13}}>No movements recorded yet.</p>}
            {hist.some(m=>m.note) && <div style={{marginTop:12,fontSize:12,color:"var(--muted)"}}>
              {hist.filter(m=>m.note).map(m=><div key={m.movement_id}>· {m.note}</div>)}</div>}
            <div className="modal-actions"><button className="btn ghost" onClick={()=>setHistFor(null)}>Close</button></div>
          </div>
        </div>
      )}
    </>
  );
}
