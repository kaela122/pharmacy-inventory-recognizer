import { useEffect, useState } from "react";
import { getUsers, addUser, editUser, delUser } from "../api";
import type { User, UserInput } from "../types";
import { ROLE_LABEL } from "../lib/auth";

const ROLES = ["admin","inventory_manager","pharmacist"];
const EMPTY:UserInput = { employee_id:"", full_name:"", role:"pharmacist", password:"" };

export default function UsersPage(){
  const [items,setItems]=useState<User[]>([]); const [err,setErr]=useState("");
  const [open,setOpen]=useState(false); const [editId,setEditId]=useState<number|null>(null);
  const [form,setForm]=useState<UserInput>(EMPTY);
  const load=()=>getUsers().then(setItems).catch(e=>setErr(e.message));
  useEffect(()=>{ load(); },[]);

  function openAdd(){ setEditId(null); setForm(EMPTY); setErr(""); setOpen(true); }
  function openEdit(u:User){ setEditId(u.user_id);
    setForm({employee_id:u.employee_id,full_name:u.full_name,role:u.role,password:""}); setErr(""); setOpen(true); }
  async function save(){
    try{ editId===null?await addUser(form):await editUser(editId,form); setOpen(false); load(); }
    catch(e){ setErr((e as Error).message); } }
  async function remove(u:User){ if(!confirm(`Delete ${u.employee_id}?`))return;
    try{ await delUser(u.user_id); load(); }catch(e){ setErr((e as Error).message); } }

  return (
    <>
      <h2 className="page-h">Users</h2>
      <div className="rowflex">
        <p className="page-sub" style={{margin:0}}>{items.length} staff accounts · admin only</p>
        <button className="btn" onClick={openAdd}>＋ Add User</button>
      </div>
      {err && <div className="err">{err}</div>}
      <div className="panel" style={{padding:0}}><table>
        <thead><tr><th>Employee ID</th><th>Name</th><th>Role</th><th></th></tr></thead>
        <tbody>{items.map(u=>(
          <tr key={u.user_id}>
            <td><span className="code">{u.employee_id}</span></td>
            <td><b>{u.full_name}</b></td>
            <td><span className="badge b-info">{ROLE_LABEL[u.role]||u.role}</span></td>
            <td style={{textAlign:"right"}}>
              <button className="btn ghost sm" onClick={()=>openEdit(u)}>Edit</button>{" "}
              <button className="iconbtn" title="Delete" onClick={()=>remove(u)}>🗑</button></td>
          </tr>
        ))}</tbody>
      </table></div>

      {open && (
        <div className="overlay" onClick={e=>e.target===e.currentTarget&&setOpen(false)}>
          <div className="modal">
            <h3>{editId===null?"Add User":"Edit User"}</h3>
            <div className="field"><label>Employee ID</label>
              <input className="mono" value={form.employee_id} disabled={editId!==null}
                placeholder="PHARM002" onChange={e=>setForm({...form,employee_id:e.target.value})}/></div>
            <div className="field"><label>Full name</label>
              <input value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></div>
            <div className="field"><label>Role</label>
              <select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}>
                {ROLES.map(r=><option key={r} value={r}>{ROLE_LABEL[r]}</option>)}</select></div>
            <div className="field"><label>{editId===null?"Password":"New password (blank = keep current)"}</label>
              <input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></div>
            <div className="modal-actions">
              <button className="btn ghost" onClick={()=>setOpen(false)}>Cancel</button>
              <button className="btn" onClick={save}>Save</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
