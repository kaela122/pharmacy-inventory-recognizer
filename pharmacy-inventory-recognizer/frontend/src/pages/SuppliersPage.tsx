import { useEffect, useState } from "react";
import { getSuppliersFull, addSupplier, editSupplier, delSupplier } from "../api";
import type { SupplierFull, SupplierInput } from "../types";
import { loadAuth } from "../lib/auth";

const EMPTY:SupplierInput = { name:"", contact_person:"", phone:"", email:"" };

export default function SuppliersPage(){
  const [items,setItems]=useState<SupplierFull[]>([]); const [q,setQ]=useState(""); const [err,setErr]=useState("");
  const [open,setOpen]=useState(false); const [editId,setEditId]=useState<number|null>(null);
  const [form,setForm]=useState<SupplierInput>(EMPTY);
  const canEdit=["admin","inventory_manager"].includes(loadAuth()?.role||"");
  const load=()=>getSuppliersFull().then(setItems).catch(e=>setErr(e.message));
  useEffect(()=>{ load(); },[]);
  const shown=items.filter(s=>`${s.name} ${s.contact_person}`.toLowerCase().includes(q.trim().toLowerCase()));

  function openAdd(){ setEditId(null); setForm(EMPTY); setErr(""); setOpen(true); }
  function openEdit(s:SupplierFull){ setEditId(s.supplier_id);
    setForm({name:s.name,contact_person:s.contact_person,phone:s.phone,email:s.email}); setErr(""); setOpen(true); }
  async function save(){ if(!form.name.trim())return;
    try{ editId===null?await addSupplier(form):await editSupplier(editId,form); setOpen(false); load(); }
    catch(e){ setErr((e as Error).message); } }
  async function remove(s:SupplierFull){ if(!confirm(`Delete ${s.name}?`))return;
    try{ await delSupplier(s.supplier_id); load(); }catch(e){ setErr((e as Error).message); } }

  return (
    <>
      <h2 className="page-h">Suppliers</h2>
      <div className="rowflex">
        <p className="page-sub" style={{margin:0}}>{items.length} suppliers</p>
        {canEdit && <button className="btn" onClick={openAdd}>＋ Add Supplier</button>}
      </div>
      {err && <div className="err">{err}</div>}
      <div className="toolbar"><div className="search">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
        <input placeholder="Search suppliers…" value={q} onChange={e=>setQ(e.target.value)}/></div></div>
      <div className="panel" style={{padding:0}}><table>
        <thead><tr><th>Supplier</th><th>Contact</th><th>Phone</th><th>Email</th><th>Orders</th><th></th></tr></thead>
        <tbody>{shown.map(s=>(
          <tr key={s.supplier_id}>
            <td><b>{s.name}</b></td>
            <td style={{color:"var(--muted)"}}>{s.contact_person||"—"}</td>
            <td className="mono" style={{fontSize:12}}>{s.phone||"—"}</td>
            <td style={{color:"var(--muted)"}}>{s.email||"—"}</td>
            <td><span className="badge b-mut">{s.order_count}</span></td>
            <td style={{textAlign:"right"}}>{canEdit && <>
              <button className="btn ghost sm" onClick={()=>openEdit(s)}>Edit</button>{" "}
              <button className="iconbtn" title="Delete" onClick={()=>remove(s)}>🗑</button></>}</td>
          </tr>
        ))}{shown.length===0 && <tr><td colSpan={6} style={{color:"var(--muted)",textAlign:"center",padding:24}}>No suppliers match.</td></tr>}</tbody>
      </table></div>

      {open && (
        <div className="overlay" onClick={e=>e.target===e.currentTarget&&setOpen(false)}>
          <div className="modal">
            <h3>{editId===null?"Add Supplier":"Edit Supplier"}</h3>
            <div className="field"><label>Supplier name</label>
              <input value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/></div>
            <div className="field"><label>Contact person</label>
              <input value={form.contact_person} onChange={e=>setForm({...form,contact_person:e.target.value})}/></div>
            <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
              <div className="field"><label>Phone</label>
                <input value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})}/></div>
              <div className="field"><label>Email</label>
                <input value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/></div>
            </div>
            <div className="modal-actions">
              <button className="btn ghost" onClick={()=>setOpen(false)}>Cancel</button>
              <button className="btn" onClick={save} disabled={!form.name.trim()}>Save</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
