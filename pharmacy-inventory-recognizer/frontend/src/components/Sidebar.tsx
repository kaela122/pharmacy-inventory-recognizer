import { ROLE_LABEL, type AuthUser } from "../lib/auth";

const I = {
  dashboard:"M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z",
  medicines:"M10.5 20.5 3.5 13.5a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7z M8 8l7 7",
  categories:"M3 7l9-4 9 4-9 4zM3 7v10l9 4 9-4V7",
  orders:"M3 3h4l2 12h10l2-8H6 M9 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2 M18 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2",
  suppliers:"M3 8h13v9H3zM16 11h4l1 3v3h-5 M6.5 21a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3 M18 21a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3",
  analytics:"M4 20V10M10 20V4M16 20v-7M22 20H2",
  recognizer:"M4 4h4V2H2v6h2zM20 4v4h2V2h-6v2zM4 20v-4H2v6h6v-2zM20 20h-4v2h6v-6h-2zM7 12h10",
  users:"M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8 M23 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75",
};
const NAV = [
  {key:"dashboard",label:"Dashboard"},{key:"medicines",label:"Medicines"},
  {key:"categories",label:"Categories"},{key:"orders",label:"Orders"},
  {key:"suppliers",label:"Suppliers"},{key:"analytics",label:"Analytics"},
  {key:"recognizer",label:"Code Recognizer"},{key:"users",label:"Users",admin:true},
];
export { NAV };

function Icon({ d }:{ d:string }){
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
    strokeLinecap="round" strokeLinejoin="round"><path d={d}/></svg>;
}

export default function Sidebar({ page, go, open, onLogout, user }:{
  page:string; go:(k:string)=>void; open:boolean; onLogout:()=>void; user:AuthUser;
}){
  const items = NAV.filter(n => !n.admin || user.role==="admin");
  return (
    <aside className={open?"open":""}>
      <div className="brand"><span className="dot">💊</span> MedIQ</div>
      <nav>{items.map(n=>(
        <button key={n.key} className={page===n.key?"active":""} onClick={()=>go(n.key)}>
          <Icon d={(I as Record<string,string>)[n.key]}/>{n.label}</button>
      ))}</nav>
      <div className="side-foot">
        <div className="side-user">
          <span className="av">{user.full_name.charAt(0)}</span>
          <div><b>{user.full_name}</b><span>{ROLE_LABEL[user.role]||user.role}</span></div>
        </div>
        <button className="signout" onClick={onLogout}>⇥ Sign out</button>
        <div className="copy">COM244 · Automata-validated pharmacy inventory</div>
      </div>
    </aside>
  );
}
